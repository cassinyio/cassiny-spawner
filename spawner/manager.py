"""
Service manager.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
import shlex
from typing import Dict, List, Tuple, Union
from uuid import uuid4

from aiodocker.docker import Docker
from aiodocker.exceptions import DockerError

from spawner.api import Api
from spawner.cargo import Cargo
from spawner.job import Job
from spawner.probe import Probe
from utils import MakeTarFromFo

log = logging.getLogger(__name__)


class ServiceManager:
    """ServiceManager class."""
    _docker = None

    def __init__(self):

        self.api = Api(self)
        self.cargo = Cargo(self)
        self.job = Job(self)
        self.probe = Probe(self)

    @property
    def docker(self):
        """Single global instance for docker client."""
        cls = self.__class__
        if cls._docker is None:
            docker = Docker()
            cls._docker = docker
        return cls._docker

    async def get_service(self, name: str):
        """Return ID of a service given the name, otherwise it would return None."""
        log.info(f"Getting docker service: {name}", )
        try:
            service = await self.docker.services.inspect(name)
        except DockerError:
            service = None
            log.warning(f"Docker service {name} is gone")

        return service

    async def create(self, *, name=None, user_id, specs, env):
        """Create a new service."""
        networks, task_template = self.create_template(user_id, specs)

        # pass envs to the service

        if env is not None:
            task_template['ContainerSpec']['Env'] = env

        params = {
            "networks": networks,
            "task_template": task_template,
        }

        if name is not None:
            params['name'] = name

        log.info(f"task_template: {task_template}")

        service = None
        if name:
            service = await self.get_service(name=name)

        if service is None:
            resp = await self.docker.services.create(**params)
            service_id = resp['ID']

            log.info(
                f"Created Docker service {service_id} "
                f"from image {task_template['ContainerSpec']['Image']}"
            )

        else:
            log.info(
                "Found existing Docker service {name} (id: {service_id[:7]})")

        return service_id[:10]

    @staticmethod
    def get_image(specs: Dict) -> str:
        """Create an URI for the given image."""
        # Use only blueprint if repository in None
        repository = specs.get('repository', None)
        blueprint = specs.get('blueprint', None)
        if repository is None:
            return f"{blueprint}"
        return f"{repository}/{blueprint}"

    def create_template(self, user_id: int, specs: Dict) -> Tuple[List, Dict]:
        """Create service template."""
        TaskTemplate = {}
        container_spec: Dict[str, Union[str, List, Dict]] = {}

        # Use only blueprint if repository in None
        container_spec['Image'] = self.get_image(specs)

        cpu = specs['cpu']
        ram = specs['ram']

        networks: List = []
        if 'networks' in specs:
            networks = specs['networks']

        # Pass the user_id to the service, the key has to be a string!
        # log_uuid is used to define a unique service among many events
        container_spec['Labels'] = {
            "user_id": str(user_id),
            "log_uuid": uuid4().hex,
        }

        # command is used when an entrypoint
        # inside the image IS NOT specified
        if "command" in specs:
            if isinstance(specs["command"], list):
                container_spec["Command"] = specs["command"][:1]
                container_spec["Args"] = specs["command"][1:]
            else:
                command = shlex.split(specs["command"])
                container_spec["Command"] = command[:1]
                container_spec["Args"] = command[1:]

        # command is used when a entrypoint
        # inside the image is specified
        if "args" in specs:
            # ["/usr/local/bin/start-singleuser.sh"],
            if isinstance(specs["args"], list):
                container_spec["Args"] = specs["args"]
            else:
                command = shlex.split(specs["args"])
                container_spec["Args"] = command

        # mounting volumes inside the service
        if 'mounts' in specs:
            container_spec['Mounts'] = []

        # add placement conditions
        placement = specs.get('placement', [])

        if "gpu" in specs:
            placement.append("node.labels.gpu == true")

        TaskTemplate['Placement'] = {'Constraints': placement}

        # Restart Policy
        restart_policy = {}
        if specs['service_type'] == "job":
            # on-failure or none
            restart_policy.update({"Condition": "none"})
        if restart_policy:
            TaskTemplate['RestartPolicy'] = restart_policy

        # https://github.com/moby/moby/issues/24713
        resources = {
            "Limits": {
                "NanoCPUs": int(cpu * 1e9),  # number of cpu
                "MemoryBytes": int(ram * 1e9)  # mem in bytes
            },
        }

        # set fluentd as a logger
        TaskTemplate['LogDriver'] = {
            "Name": "fluentd",
            "Options": {
                "fluentd-async-connect": "true",
                "labels": "com.docker.swarm.service.name,user_id,log_uuid"
            }
        }

        TaskTemplate['ContainerSpec'] = container_spec
        TaskTemplate['Resources'] = resources

        return networks, TaskTemplate

    async def build_and_push_from_fo(self, file_object, tag, blueprint):
        """Build and image from a file-like-object."""
        stream = await self.docker.build(fileobj=file_object, tag=tag)
        async for output in stream:
            try:
                print(output['stream'].strip())
            # stream is not available when you download images
            except KeyError:
                pass
        await self.docker.push(tag)

    async def build_and_push_from_s3(self, s3_key, s3_skey, cargo, image, tag, bucket='default'):
        """Build and image from s3."""
        async with MakeTarFromFo(
            cargo=cargo,
            bucket=bucket,
            s3_key=s3_key,
            s3_skey=s3_skey,
            image=image
        ) as tar_file:

            stream = await self.docker.docker.images.build(
                fileobj=tar_file,
                nocache=True,
                encoding="gzip",
                tag=tag,
                stream=True
            )

            async for output in stream:
                try:
                    print(output['stream'].strip())
                # stream is not available when you download images
                except KeyError:
                    pass

        stream = await self.docker.push(tag)
        async for output in stream:
            print(output)

    async def remove(self, name: str = None, uuid: str = None):
        """Remove a service from Docker."""
        if name is None:
            name = uuid

        if name is None:
            raise KeyError(
                "You need to specify a uuid or a name to remove a service")

        log.info(f"Stopping and removing docker service {name}")
        resp = None

        try:
            resp = await self.docker.services.delete(name)
            log.info(f"Docker service {name} removed")
        except DockerError:
            log.exception(f"Docker service {name} doesn't exist")

        return resp

    async def build(self, tag: str, fileobj):
        """
        Logs from the service
        Consider using stop/start when Docker adds support
        """

        log.info(f"Building image of {tag}")

        try:
            image = await self.docker.images.build(
                fileobj=fileobj,
                encoding="gzip",
                tag=tag,
                stream=True)
        except DockerError:
            log.exception(f"Error while building {tag}")
        else:
            return image

    async def push(self, name):
        try:
            image = await self.docker.images.push(name=name, stream=True)
        except DockerError:
            log.exception(f"Error while pushing {name}")
        else:
            return image
