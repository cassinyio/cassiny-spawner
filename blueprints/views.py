"""
Blueprints views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging

from aiohttp.web import json_response
from sqlalchemy.sql import select

from blueprints.models import mBlueprint
from blueprints.serializers import BlueprintSchema
from utils import WebView, verify_token

log = logging.getLogger(__name__)


class Blueprint(WebView):
    """Views to handle blueprints."""

    @verify_token
    async def get(self, user_id):

        async with self.db.acquire() as conn:
            query = select([mBlueprint])\
                .where(
                    (mBlueprint.c.public.is_(True)) |
                    (mBlueprint.c.user_id == user_id)
            )
            result = await conn.execute(query)
            blueprints = await result.fetchall()

        blueprint_schema = BlueprintSchema(many=True)
        blueprints = blueprint_schema.dump(blueprints)

        return json_response({"blueprints": blueprints.data})
