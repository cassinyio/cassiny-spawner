"""
Logs views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""


from aiohttp.web import json_response
from sqlalchemy.sql import select

from events.models import mLog
from events.serializers import Logs as LogsSchema
from utils import WebView, verify_token


class Events(WebView):
    """Views to handle events."""

    @verify_token
    async def get(self, payload):
        user_id = payload["user_id"]
        async with self.db.acquire() as conn:
            query = select([
                mLog.c.name,
                mLog.c.user_id,
                mLog.c.uuid,
                mLog.c.action,
                mLog.c.created_at,
            ])\
                .where(
                (mLog.c.user_id == user_id) &
                ((mLog.c.action == 'create') |
                 (mLog.c.action == 'die'))
            )\
                .order_by(mLog.c.created_at.desc())\
                .limit(50)

            result = await conn.execute(query)
            logs = await result.fetchall()

        log_schema = LogsSchema(many=True)
        data, errors = log_schema.dump(logs)

        return json_response({"logs": data})


class Logs(WebView):
    """Views to get Logs."""

    @verify_token
    async def get(self, payload):
        is_owner = 0
        if is_owner:
            logs = self.docker.service.logs("service_name")
            return json_response({"logs": logs})

        return json_response({"logs": logs})
