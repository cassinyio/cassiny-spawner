"""Blueprint controller."""

import logging
from typing import Dict

from spawner.base_service import BaseService

log = logging.getLogger(__name__)


class Blueprint(BaseService):
    """Blueprint creator."""

    def __init__(self, spawner) -> None:
        self._spawner = spawner

    async def create(self, name: str, fileobj: Dict):
        """
        Create a new job as a Docker service.

        Parameters
        -----------
        tag
            unique name for the probe.
        fileobj
            user id.


        """
        service_id = await self._spawner.build(
            name=name,
            fileobj=fileobj,
        )

        #service_id = await self._spawner.push(name=name)
        return service_id

    async def push(self, name: str, username: str, password: str):
        """
        Push a docker image to a registry.
        """
        auth = {"username": username, "password": password}
        service_id = await self._spawner.push(name=name, auth=auth)
        return service_id
