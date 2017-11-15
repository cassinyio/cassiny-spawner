"""
Job controller.

"""

import logging
from typing import Dict

log = logging.getLogger(__name__)


class Job():
    """Manage jobs creation and desctruction"""

    def __init__(self, spawner):
        self._spawner = spawner
        self.name = None

    async def create(self, name: str, user_id: int, specs: Dict):
        """
        Create a new job as a Docker service.

        Parameters
        -----------
        specs: specs about how to build the Docker service.
        """
        env = self.get_env(name)
        service_id = await self._spawner.create(
            name=name,
            user_id=user_id,
            specs=specs,
            env=env
        )

        return service_id

    async def remove(self, name: str):
        """Delete a job."""
        response = await self._spawner.remove(name=name)
        return response

    @staticmethod
    def get_env(name):
        """Add env variables to the service."""
        env = {"JOB_ID": name}
        return env
