"""
API controller.

"""


import logging
from typing import Dict
from uuid import uuid4

log = logging.getLogger(__name__)


class Api():
    """A container for a API."""

    def __init__(self, spawner):
        self._spawner = spawner

    async def create(
            self, name: str, user_id: int,
            specs: Dict, cargo, s3_key: str, s3_skey: str):
        """
        Create a new API as a Docker service.
        Also add a route to Redis.

        specs: specs about how to build the Docker service.
        """

        image = self._spawner.get_image(specs)

        # we build an image for the user
        registry_ = 'registry.cassiny.io'
        repo_ = "username"
        image_ = "image_name"
        tag_ = uuid4().hex[:10]
        tag = f"{registry_}/{repo_}/{image_}:{tag_}"

        await self._spawner.build_and_push_from_s3(
            cargo=cargo,
            s3_key=s3_key,
            s3_skey=s3_skey,
            image=image,
            tag=tag
        )

        # we launch the specific image
        specs['repository'], specs['blueprint'] = (
            f"{registry_}", f"{repo_}/{image_}:{tag_}")

        env = self.get_env(name)

        try:
            await self._spawner.create(name=name, user_id=user_id, specs=specs, env=env)
            return True
        except Exception:
            log.exception("Errow while creating probe.")
            return False

    def add_mounts(self):

        mounts = [{'type': 'volume',
                   'source': 'volume1',
                   'target': '/home/user/work', }]

        return mounts

    async def remove(self, name: str):
        """
        Delete an API.
        Remove both docker service, redis and route inside the db.
        """
        response = await self._spawner.remove(name=name)
        return response

    @staticmethod
    def get_env(name):
        env = {
            "API_ID": name
        }

        return env
