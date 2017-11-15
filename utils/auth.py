"""
Utils for auth.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import functools
import logging
from typing import Mapping, Optional

import jwt
from aiohttp import web
from aiohttp.abc import AbstractView
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
)

from config import Config as C

log = logging.getLogger(__name__)


async def _validate_token(headers: Mapping, key: str=C.PUBLIC_KEY) -> Optional[int]:
    """Validate the token inside the headers.

    Return the user_id if correct, None in the other cases.
    """
    user_id = None
    if "Authorization" in headers:
        try:
            encoded = headers['Authorization'].split('Bearer ')[1]
            paylod = jwt.decode(encoded, key)
            user_id = paylod['user_id']
        except (IndexError, DecodeError, ExpiredSignatureError):
            log.info(f"Attempt to login with non valid/expired token")

    return user_id


def verify_token(func):
    """Check if the given jws token is valid."""
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):

        # Supports class based views see web.View
        if isinstance(args[0], AbstractView):
            request = args[0].request
        else:
            request = args[-1]

        # check if user is logged
        user_id = await _validate_token(request.headers)

        if user_id is None:
            message = "Session expired"
            return web.json_response({"message": message}, status=401)
        else:
            response = await func(*args, user_id=user_id, **kwargs)
            return response
    return wrapped
