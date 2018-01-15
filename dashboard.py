"""
    dashboard.py
    ~~~~~~~~~
    Dashboard views

    :copyright: (c) 2017, Cassiny.io OÜ.
    All rights reserved.
"""

from datetime import datetime
from uuid import uuid4

import aiohttp
import aiohttp_jinja2
from aiohttp.web import json_response
from sqlalchemy.sql import and_, func, or_, select

import ujson
from auth import models as aModels
from auth.utils import login_required, verify_token
from service.apis.models import mApi
from service.blueprints.models import mBlueprint
from service.jobs.models import mJob
from service.probes.models import mProbe, mProbeRoutes
from utils import WebView

from . import serializers

# Dashboard
('GET', '/api/v1/dashboard', Dashboard, 'ApiDashboard'),

class Dashboard(WebView):
    """
    Views to handle blueprint
    """

    @verify_token
    async def get(self, payload):
        payload = payload["user_id"]

        async with self.db.acquire() as conn:
            query = select([
                mProbe
            ])\
            .where(mProbe.c.user_id == user_id)\
            .select_from(
                mProbe
                .join(mProbeRoutes, mProbe.c.name == mProbeRoutes.c.subdomain)
            )
            probe = await conn.execute(query)

            query = mJob.select().where(
                mJob.c.user_id == user_id,
            )
            jobs = await conn.execute(query)

            query = mApi.select().where(
                mApi.c.user_id == user_id,
            )
            apis = await conn.execute(query)

        message = {
            "probes": probe.rowcount,
            "jobs": jobs.rowcount,
            "apis": apis.rowcount,
        }

        return json_response(message)
