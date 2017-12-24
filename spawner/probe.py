"""
Probes controller.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


import logging
from typing import Any, Dict
from urllib.parse import urlparse

from config import Config as C
from spawner.base_service import BaseService

log = logging.getLogger(__name__)


class Probe(BaseService):
    """Probe spawner."""

    async def create(
        self,
        *,
        name: str,
        user_id: int,
        specs: Dict,
        token: str,
    ) -> bool:
        """
        Create a new probe as a Docker service.

        Parameters
        -----------
        name
            unique name for the probe.
        user_id
            user id.
        specs
            specs about how to build the Docker service.

        """
        env = self.get_env(name=name, token=token)

        specs.update({
            "service_type": "probe",
            "networks": ["cassiny-public"],
        })

        # service labels
        service_labels = {
            "traefik.port": f'{env["PROBE_PORT"]}',
            "traefik.enable": "true",
            "traefik.frontend.rule": C.TRAEFIK_RULE.format(name),
            "traefik.docker.network": specs["networks"][-1],
        }

        service = await self._spawner.create(
            name=name, user_id=user_id, specs=specs, env=env, service_labels=service_labels
        )
        return service

    @staticmethod
    def get_env(name: str, token: str) -> Dict[str, Any]:
        """
        Return a dict of env vars.

        Parameters
        -----------
        name
            name for the service.
        token
            token to secure jupyter access.
            http://jupyter-notebook.readthedocs.io/en/stable/security.html

        """
        url = urlparse(C.PROBE_DEFAULT_URL)
        env = {
            "JPY_USER": "user",
            "PROBE_IP": url.hostname,
            "PROBE_PORT": url.port,
            "PROBE_NAME": name,
            "PROBE_TOKEN": token,
        }
        return env
