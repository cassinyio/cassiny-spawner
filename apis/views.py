"""
APIs views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
from typing import Mapping, Union
from uuid import uuid4

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.sql import select

from apis.models import mApi
from apis.serializers import APIs as ApiSchema
from blueprints.models import mBlueprint
from cargos.models import mCargo
from utils import WebView, check_quota, verify_token

log = logging.getLogger(__name__)


class APIs(WebView):
    """Create api and push api online."""

    @verify_token
    async def get(self, payload: Mapping[str, Union[str, int]]):
        """Get a list of APIs for the current user."""
        user_id = payload['user_id']
        async with self.db.acquire() as conn:
            query = select([
                mApi,
                mCargo.c.name.label("cargo_name"),
                mBlueprint.c.name.label("blueprint_name"),
                mBlueprint.c.repository.label("blueprint_repository"),
            ])\
                .where(mApi.c.user_id == user_id)\
                .select_from(
                    mApi
                    .outerjoin(mCargo, mApi.c.cargo_id == mCargo.c.id)
                    .outerjoin(mBlueprint, mApi.c.blueprint_id == mBlueprint.c.id)
            )

            result = await conn.execute(query)
            apis = await result.fetchall()

        data, errors = ApiSchema(many=True).dump(apis)

        if errors:
            return json_response(errors, status=400)

        body = {"apis": data}
        return json_response(body)

    @verify_token
    @check_quota(mApi)
    async def post(self, payload: Mapping[str, Union[str, int]]):
        """Create a new API endpoint."""
        user_id = payload['user_id']
        data = await self.request.json()

        data, errors = ApiSchema().load(data)

        if errors:
            log.warning(
                f"Error while handling request from user {user_id}: {errors}")
            body = {"message": errors}
            return json_response(body, status=400)

        # create event
        event = {
            "user_id": user_id,
            "specs": data
        }
        await streaming.publish("service.api.create", event)

        message = "We are creating your API......."
        body = {"message": message}
        return json_response(body)

    @verify_token
    async def delete(self, payload: Mapping[str, Union[str, int]]):
        """Delete an API endpoint given an id."""
        user_id = payload['user_id']
        # get the api_id from the url path
        api_id = self.request.match_info.get("api_id")

        log.info(f"Request to delete API ({api_id}) from user ({user_id}")

        async with self.db.acquire() as conn:
            query = mApi.delete()\
                .where(
                    (mApi.c.user_id == user_id) &
                    (mApi.c.id == api_id)
            ).returning(
                mApi.c.name
            )
            result = await conn.execute(query)
            # returns None if api_id doesn't exist
            deleted_api = await result.fetchone()

        if deleted_api is not None:
            event = {
                "user_id": user_id,
                "event_uuid": uuid4().hex,
                "name": deleted_api.name,
            }

            await streaming.publish("service.api.delete", event)

            user_message = f"We are removing {deleted_api.name}"
            body = {"message": user_message}
            return json_response(body)

        message = f"User has tried to remove an API that doesn't exist inside the database: {api_id}"
        log.error(message)
        user_message = f"It seems that api doesn't exist anymore."
        body = {"message": user_message}
        return json_response(body)
