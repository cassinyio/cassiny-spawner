"""
Collection of utils for Views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from typing import Dict

import msgpack
from aiohttp import web

from config import Config


async def send_event(events_queue, routing_key: str, message: Dict):
    """
    Send events to a given queue.

    :route_key: a str with the route key
    :message: a dict that will be msgpacked
    """
    body = msgpack.packb(message)

    await events_queue.send_and_wait(routing_key, body)


class WebView (web.View):
    """Subclass of web.View to pass some properties to all the views.

    Specifically we want to pass the redis, db and logger
    They are defined inside app.py
    """

    @property
    def config(self):
        return Config

    @property
    def redis(self):
        return self.request.app["redis"]

    @property
    def db(self):
        return self.request.app["db"]

    async def send_event(self, routing_key: str, message: Dict):
        """
        Send events to a given queue.

        :route_key: a str with the route key
        :message: a dict that will be msgpacked
        """
        await send_event(
            self.request.app["events_queue"],
            routing_key=routing_key,
            message=message)

    async def query_db(self, query, many=False, get_result=True):
        """Simplify calling the db."""
        async with self.db.acquire() as conn:
            result = await conn.execute(query)
            if get_result:
                if not many:
                    row = await result.fetchone()
                    return row
                rows = await result.fetchall()
                return rows
