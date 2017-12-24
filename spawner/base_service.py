"""Base service."""


import logging

log = logging.getLogger(__name__)


class BaseService():
    """Base class for services."""

    def __init__(self, spawner) -> None:
        self._spawner = spawner

    async def delete(self, name: str):
        """Delete a service."""
        response = await self._spawner.remove(name=name)
        return response
