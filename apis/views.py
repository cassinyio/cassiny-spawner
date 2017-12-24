"""
APIs views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.exc import InterfaceError, InternalError
from sqlalchemy.sql import select, update

from apis.models import mApi
from apis.serializers import APIs as ApiSchema
from blueprints.models import mBlueprint
from config import Config as C
from spawner import Spawner
from utils import (
    WebView,
    check_quota,
    naminator,
    verify_token,
)

log = logging.getLogger(__name__)


class APIs(WebView):
    """Create api and push api online."""

    @verify_token
    async def get(self, payload: Mapping[str, Any]):
        """Get a list of APIs for the current user."""
        user_id = payload['user_id']
        async with self.db.acquire() as conn:
            query = select([
                mApi,
                mBlueprint.c.name.label("blueprint_name"),
                mBlueprint.c.repository.label("blueprint_repository"),
            ])\
                .where(mApi.c.user_id == user_id)\
                .select_from(
                    mApi
                    .outerjoin(mBlueprint, mApi.c.blueprint_id == mBlueprint.c.id)
            )

            result = await conn.execute(query)
            apis = await result.fetchall()

        apis = ApiSchema(many=True).dump(apis)

        body = {"apis": apis.data}
        return json_response(body)

    @verify_token
    @check_quota(mApi)
    async def post(self, payload: Mapping[str, Any]):
        """Create a new API."""
        user_id = payload['user_id']
        data = await self.request.json()

        data, errors = ApiSchema().load(data)
        if errors:
            return json_response({"error": errors}, status=400)

        query = mBlueprint.select().where(
            (mBlueprint.c.id == data['blueprint_id']) &
            (
                (mBlueprint.c.user_id == user_id) |
                (mBlueprint.c.public.is_(True))
            )
        )
        blueprint = await self.query_db(query)

        if blueprint is None:
            log.error(data)
            error = "Did you select the right blueprint?"
            return json_response({"error": error}, status=400)

        name = naminator("api")
        cpu, ram, gpu = C.SIZE[data['machine_type']]

        specs = {
            'repository': blueprint.repository,
            'blueprint': ":".join((blueprint.name, blueprint.tag)),
            'networks': ["cassiny-public"],
            'machine_type': data['machine_type'],
            'cpu': cpu,
            'ram': ram,
            'gpu': gpu
        }

        try:
            query = mApi.insert().values(
                user_id=user_id,
                blueprint_id=blueprint.id,
                name=name,
                description=data['description'],
                specs=specs,
            )
            await self.query_db(query, get_result=False)
        except InterfaceError:
            return json_response({"error": errors}, status=400)

        service = await Spawner.api.create(
            name=name,
            user_id=user_id,
            specs=specs
        )

        if not service:
            try:
                query = update(mApi).where(
                    mApi.c.name == name).values(status=3)
                await self.query_db(query, get_result=False)
            except InternalError:
                log.exception(f"Error while saving status for {name}.")
            finally:
                message = f"There's been an error while creating {name}."
                return json_response({"error": message}, status=400)

        message = f"we are creating {name}."
        return json_response({"message": message})

    @verify_token
    async def delete(self, payload: Mapping[str, Any]):
        """Delete an API."""
        user_id = payload['user_id']
        api_id = self.request.match_info.get("api_id")

        try:
            query = mApi.delete()\
                .where(
                (mApi.c.user_id == user_id) &
                (mApi.c.id == int(api_id))
            )
        except ValueError:
            query = mApi.delete()\
                .where(
                (mApi.c.user_id == user_id) &
                (mApi.c.name == api_id)
            )

        async with self.db.acquire() as conn:
            result = await conn.execute(query.returning(mApi.c.name))
            deleted_api = await result.fetchone()

        if deleted_api is None:
            log.error(f"API doesn't exist inside the database: {api_id}")
            user_message = f"It seems that api doesn't exist anymore."
            return json_response({"error": user_message}, status=400)

        result = await Spawner.api.delete(name=deleted_api.name)
        event = {
            "user_id": user_id,
            "name": deleted_api.name,
        }
        await streaming.publish("service.api.deleted", event)
        user_message = f"We are removing {deleted_api.name}"
        return json_response({"error": user_message})
