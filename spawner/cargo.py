"""Cargo controller."""


import logging
from typing import Dict
from urllib.parse import urlparse

from config import Config as C
from spawner.base_service import BaseService

log = logging.getLogger(__name__)


class Cargo(BaseService):
    """Cargo spawner."""

    async def create(
        self,
        name: str,
        user_id: int,
        specs: Dict,
        access_key: str,
        secret_key: str
    ) -> bool:
        """
        Create a new cargo service.

        Parameters
        -----------
        name
            unique name for the probe.
        user_id
            user id.
        specs
            specs about how to build the Docker service.
        access_key
            specs about how to build the Docker service.
        secret_key
            specs about how to build the Docker service.

        """
        env = self.get_env(
            name=name,
            access_key=access_key,
            secret_key=secret_key
        )

        url = urlparse(C.CARGO_DEFAULT_URL)

        specs.update({
            'args': "server /data",
            'repository': "minio",
            'blueprint': "minio:RELEASE.2017-11-22T19-55-46Z",
            'networks': ["cassiny-public"],
            'service_type': "cargo"
        })

        service_labels = {
            "traefik.port": f'{url.port}',
            "traefik.enable": "true",
            "traefik.frontend.rule": C.TRAEFIK_RULE.format(name),
            "traefik.docker.network": specs["networks"][-1],
        }

        # cargos have the constraint to be run on storage servers
        constraint = "node.labels.type == storage"
        if 'placement' in specs:
            specs['placement'].append(constraint)
        else:
            specs['placement'] = [constraint]

        service_id = await self._spawner.create(
            name=name, user_id=user_id, specs=specs,
            env=env, service_labels=service_labels
        )
        return service_id

    @staticmethod
    def get_env(
        name: str,
        access_key: str,
        secret_key: str
    ) -> Dict[str, str]:
        """
        Return a dict of env vars.

        Parameters
        -----------
        name
            name for the service.
        access_key
            access key for minio.
        secret_key
            secret key for minio.

        """
        env = {
            "MINIO_BROWSER": "off",
            "MINIO_ACCESS_KEY": access_key,
            "MINIO_SECRET_KEY": secret_key,
            "CARGO_NAME": name,
        }
        return env
