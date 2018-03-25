"""API spawner."""


import logging
from typing import Dict
from urllib.parse import urlparse

from config import Config as C
from spawner.base_service import BaseService

log = logging.getLogger(__name__)


class Api(BaseService):
    """APIs services controller."""

    async def create(
        self,
        name: str,
        user_id: int,
        specs: Dict,
    ) -> bool:
        """
        Create a new API as a Docker service.

        specs: specs about how to build the Docker service.
        """
        env = self.get_env(name)
        specs['service_type'] = "api"

        url = urlparse(C.API_DEFAULT_URL)

        # service labels
        service_labels = {
            "traefik.port": f"{url.port}",
            "traefik.enable": "true",
            "traefik.frontend.rule": C.TRAEFIK_RULE.format(name),
            "traefik.docker.network": specs["networks"][-1],
        }

        service = await self._spawner.create(
            name=name, user_id=user_id,
            specs=specs, env=env, service_labels=service_labels
        )
        log.info(f"{specs['service_type']}({name}) created.")
        return service

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
            "API_NAME": name
        }

        return env
