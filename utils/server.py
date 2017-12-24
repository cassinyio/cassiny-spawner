"""
Collection of utils for Views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from aiohttp import web

from config import Config


class WebView (web.View):
    """Subclass of web.View to pass some properties to all the views.

    Specifically we want to pass the redis, db and logger
    They are defined inside app.py
    """

    @property
    def config(self):
        """Return config object."""
        return Config

    @property
    def db(self):
        """DB pool object."""
        return self.request.app["db"]

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
