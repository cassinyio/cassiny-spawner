"""Job controller."""

import logging
from typing import Dict

from spawner.base_service import BaseService

log = logging.getLogger(__name__)


class Job(BaseService):
    """Job spawner."""

    def __init__(self, spawner) -> None:
        self._spawner = spawner

    async def create(self, name: str, user_id: int, specs: Dict) -> bool:
        """
        Create a new job as a Docker service.

        Parameters
        -----------
        name
            unique name for the probe.
        user_id
            user id.
        specs
            specs about how to build the Docker service.

        """
        env = self.get_env(name)
        specs['service_type'] = "job"

        service_id = await self._spawner.create(
            name=name,
            user_id=user_id,
            specs=specs,
            env=env
        )
        return service_id

    @staticmethod
    def get_env(name: str) -> Dict[str, str]:
        """
        Return a dict of env vars.

        Parameters
        -----------
        name
            name for the service.

        """
        env = {
            "JOB_NAME": name
        }
        return env
