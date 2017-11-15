"""Cargo controller."""


import logging
from typing import Dict

log = logging.getLogger(__name__)


class Cargo():
    """A container for cargo"""

    def __init__(self, spawner):
        self._spawner = spawner

    async def create(
        self, name: str, user_id: int,
        specs: Dict, access_key: str, secret_key: str
    ) -> bool:
        """
        Create a new probe as a Docker service.

        specs: specs about how to build the Docker service.
        """

        # keys used to access the S3
        env = self._get_env(access_key=access_key, secret_key=secret_key)

        # cargos have the constraint to be run on storage servers
        # they are labeled with spacedock
        constraint = "node.labels.type == storage"
        if 'placement' in specs:
            specs['placement'].append(constraint)
        else:
            specs['placement'] = [constraint]

        service_id = await self._spawner.create(name=name, user_id=user_id, specs=specs, env=env)
        return service_id

    def add_mounts(self, mount_point=None):
        '''Add mounting point for the service.'''

        # binding /export container dir on /spacedock
        mounts = [{'type': 'bind',
                   'source': '/export',
                   'target': '/spacedock/user_something', }]

        # create a local named volume
        mounts = [{'type': 'volume',
                   'source': 'name_of_the_cargo',
                   'target': '/spacedock/user_something', }]

        return mounts

    async def remove(self, name: str):
        """Delete a cargo."""
        response = await self._spawner.remove(name=name)
        return response

    @staticmethod
    def _get_env(access_key: str, secret_key: str) -> Dict[str, str]:
        env = {
            "MINIO_BROWSER": "on",
            "MINIO_ACCESS_KEY": access_key,
            "MINIO_SECRET_KEY": secret_key,
        }
        return env
