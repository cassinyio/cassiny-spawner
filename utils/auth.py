"""
Utils for auth.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import functools
import logging
from types import MappingProxyType
from typing import Any, Mapping, Optional

import jwt
from aiohttp import web
from aiohttp.abc import AbstractView
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
)

from config import Config as C

log = logging.getLogger(__name__)


def _validate_token(headers: Mapping, key: bytes=C.PUBLIC_KEY) -> Optional[Mapping[str, Any]]:
    """Validate the token inside the headers.

    Return the payload if correct, None in the other cases.
    The payload contains the token.
    """
    payload: Optional[Mapping[str, Any]] = None
    if "Authorization" in headers:
        try:
            encoded: str = headers['Authorization'].split('Bearer ')[1]
            data = jwt.decode(encoded, key)
            payload = {**data, "token": encoded}
        except (IndexError, DecodeError, ExpiredSignatureError):
            log.info(f"Attempt to login with non valid/expired token.")
    return payload


def verify_token(func):
    """Check if the given jwt is valid."""
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):

        # Supports class based views see web.View
        if isinstance(args[0], AbstractView):
            request = args[0].request
        else:
            request = args[-1]

        # check if user is logged
        payload = _validate_token(request.headers)

        if payload is None:
            message = "Your token is not valid."
            return web.json_response({"error": message}, status=401)
        else:
            payload = MappingProxyType(payload)
            response = await func(*args, payload=payload, **kwargs)
            return response
    return wrapped
