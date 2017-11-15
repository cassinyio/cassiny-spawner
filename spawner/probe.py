"""
Probe controller.

"""


import logging
from typing import Dict

from config import Config as C

log = logging.getLogger(__name__)


class Probe():
    """A container for a probe"""

    def __init__(self, spawner):
        self._spawner = spawner

    async def create(
            self, name: str, user_id: int,
            specs: Dict) -> bool:
        """
        Create a new probe as a Docker service.
        Also add a route to Redis.

        specs: specs about how to build the Docker service.
        """

        env = self.get_env(name)

        try:
            await self._spawner.create(name=name, user_id=user_id, specs=specs, env=env)
            return True
        except Exception:
            log.exception("Errow while creating probe.")
            return False

    async def remove(self, name: str):
        """
        Delete a probe.
        Remove both docker service, redis and route inside the db.
        """
        response = await self._spawner.remove(name=name)
        return response

    @staticmethod
    def get_env(name: str) -> Dict[str, str]:
        env = {
            "JPY_USER": "user",
            "COOKIE_USER_SESSION": C.PROBE_SESSION,
            "PROBE_BASE_URL": C.PROBE_DEFAULT_URL,
            "MCC_PUBLIC_URL": C.MCC_PUBLIC_URL,
            "MCC_INTERNAL_URL": C.MCC_INTERNAL_URL,
            "PROBE_NAME": name
        }

        return env
