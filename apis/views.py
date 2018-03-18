"""
APIs views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming

from apis.models import delete_api, mApi
from apis.serializers import APIs as ApiSchema
from blueprints.models import join_blueprints_with
from spawner import Spawner
from utils import WebView, get_uuid, verify_token

log = logging.getLogger(__name__)


class APIs(WebView):
    """Create api and push api online."""

    @verify_token
    async def get(self, payload: Mapping[str, Any]):
        """Get a list of APIs for the current user."""
        user_id = payload['user_id']

        apis = await join_blueprints_with(model=mApi, db=self.db, user_id=user_id)
        apis_schema = ApiSchema(many=True)
        apis_schema.context = {"user": user_id}

        data, errors = apis_schema.dump(apis)

        if errors:
            return json_response({"error": errors}, status=400)

        return json_response({"apis": data})

    @verify_token
    async def post(self, payload: Mapping[str, Any]):
        """Create a new API."""
        user_id = payload['user_id']
        data = await self.request.json()

        data, errors = ApiSchema().load(data)
        if errors:
            log.debug(errors)
            return json_response({"error": errors}, status=400)

        event = {
            "uuid": get_uuid().hex,
            "user_id": user_id,
            "data": data
        }

        await streaming.publish("service.api.create", event)
        log.info(f"Published event `service.api.create`: {event}")

        return json_response({"message": "We are creating your API."})

    @verify_token
    async def delete(self, payload: Mapping[str, Any]):
        """Delete an API."""
        user_id = payload['user_id']
        api_ref = self.request.match_info.get("api_ref")

        deleted_api = await delete_api(db=self.db, api_ref=api_ref, user_id=user_id)

        if deleted_api is None:
            log.info(f"API doesn't exist inside the database: {api_ref}")
            user_message = f"It seems that api doesn't exist anymore."
            return json_response({"error": user_message}, status=400)

        await Spawner.api.delete(name=deleted_api.name)
        event = {
            "user_id": user_id,
            "name": deleted_api.name,
        }
        await streaming.publish("service.api.deleted", event)
        user_message = f"We are removing {deleted_api.name}"
        return json_response({"message": user_message})
