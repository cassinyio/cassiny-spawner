"""
Utils for quota.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Mapping

from aiohttp import ClientSession, web
from aiohttp.abc import AbstractView
from sqlalchemy import Table, func, select

from config import Config as C

log = logging.getLogger(__name__)


async def _get_limits(token: str) -> Mapping[str, Any]:
    """Check the limits with the service."""
    headers = {"Authorization": f"Bearer {token}"}
    data: Mapping[str, Any] = {}
    try:
        async with ClientSession() as session:
            async with session.get(C.QUOTA_URI, headers=headers) as resp:
                data = await resp.json()
    except asyncio.TimeoutError:
        log.error("Timeout error while calling cassiny-billing.")
        data = {
            "message": "We have some problem in contacting one of our services. Please try later."}
    return data


def check_quota(model: Table) -> Callable:
    """Check if the quota is respected."""
    def wrapper(function: Callable) -> Callable:
        @functools.wraps(function)
        async def decorator(*args, payload, **kwargs) -> Callable:
            # if quota IS NOT active we return the decorated function directly
            if C.QUOTA_IS_ACTIVE is False:
                response = await func(*args, payload=payload, **kwargs)
                return response

            # Supports class based views see web.View
            if isinstance(args[0], AbstractView):
                request = args[0].request
            else:
                request = args[-1]

            # dictionary that contains limits for the current user
            data = await _get_limits(payload['token'])

            if model.name in data:
                limit = data[model.name]

                async with request.app["db"].acquire() as conn:
                    query = select([model]).where(
                        model.c.user_id == payload['user_id']
                    )
                    result = await conn.execute(query)

                if result.rowcount < limit:
                    response = await function(*args, payload=payload, **kwargs)
                    return response
            return web.json_response(data, status=401)
        return decorator
    return wrapper
