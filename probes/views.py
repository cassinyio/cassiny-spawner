"""
Probes views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
from secrets import token_urlsafe
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.exc import InterfaceError, InternalError
from sqlalchemy.sql import select, update

from blueprints.models import mBlueprint
from config import Config as C
from probes.models import mProbe
from probes.serializers import ProbeSchema
from spawner import Spawner
from utils import (
    WebView,
    check_quota,
    naminator,
    verify_token,
)

log = logging.getLogger(__name__)

type_payload = Mapping[str, Any]


class Probe(WebView):
    """Get info, create and remove probes."""

    @verify_token
    async def get(self, payload: type_payload):
        """Get probes."""
        user_id = payload['user_id']
        probe_id = self.request.match_info.get("probe_id")

        if probe_id:
            query = select([
                mProbe,
                mBlueprint.c.name.label("blueprint_name"),
                mBlueprint.c.repository.label("blueprint_repository"),
            ])\
                .where(
                    (mProbe.c.user_id == user_id) &
                    (mProbe.c.id == probe_id)
            ).select_from(
                mProbe.outerjoin(
                    mBlueprint, mProbe.c.blueprint_id == mBlueprint.c.id)
            )
            probe = await self.query_db(query)
            probes_schema = ProbeSchema()
            probes_schema.context = {"user": user_id}
            data, _ = probes_schema.dump(probe)

            return json_response({"probe": data})

        query = select([
            mProbe,
            mBlueprint.c.name.label("blueprint_name"),
            mBlueprint.c.repository.label("blueprint_repository"),
        ])\
            .where(mProbe.c.user_id == user_id)\
            .select_from(
            mProbe.outerjoin(
                mBlueprint, mProbe.c.blueprint_id == mBlueprint.c.id)
        )
        probes = await self.query_db(query, many=True)

        probes_schema = ProbeSchema(many=True)
        probes_schema.context = {"user": user_id}
        data, _ = probes_schema.dump(probes)

        return json_response({"probes": data})

    @verify_token
    @check_quota(mProbe)
    async def post(self, payload: type_payload):
        """Create new probes."""
        user_id = payload["user_id"]
        data = await self.request.json()

        data, errors = ProbeSchema().load(data)
        if errors:
            return json_response({"error": errors}, status=400)

        try:
            query = mBlueprint.select()\
                .where(
                (mBlueprint.c.id == data['blueprint']) &
                (
                    (mBlueprint.c.user_id == user_id) |
                    (mBlueprint.c.public.is_(True))
                )
            )
        except ValueError:
            query = mBlueprint.select()\
                .where(
                (mBlueprint.c.id == data['blueprint']) &
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

        cpu, ram, gpu = C.SIZE[data['machine_type']]

        specs = {
            'repository': blueprint.repository,
            'blueprint': f"{blueprint.name}:{blueprint.tag}",
            'machine_type': data['machine_type'],
            'cpu': cpu,
            'ram': ram,
            'gpu': gpu
        }

        name = naminator("probe")
        token = token_urlsafe(30)

        try:
            query = mProbe.insert().values(
                user_id=user_id,
                blueprint_id=blueprint.id,
                name=name,
                token=token,
                description=data['description'],
                specs=specs,
            )
            await self.query_db(query, get_result=False)
        except InterfaceError:
            return json_response({"error": errors}, status=400)

        service = await Spawner.probe.create(
            name=name,
            user_id=user_id,
            specs=specs,
            token=token,
        )

        if not service:
            try:
                query = update(mProbe).where(
                    mProbe.c.name == name).values(status=3)
                await self.query_db(query, get_result=False)
            except InternalError:
                log.exception(f"Error while saving status for {name}.")
            finally:
                message = f"There's been an error while creating {name}."
                return json_response({"error": message}, status=400)

        message = f"we are creating {name}."
        return json_response({"message": message})

    @verify_token
    async def delete(self, payload: type_payload):
        """Delete probes."""
        probe_id = self.request.match_info.get("probe_id")
        user_id = payload['user_id']

        try:
            query = mProbe.delete()\
                .where(
                (mProbe.c.user_id == user_id) &
                (mProbe.c.id == int(probe_id))
            )
        except ValueError:
            query = mProbe.delete()\
                .where(
                (mProbe.c.user_id == user_id) &
                (mProbe.c.name == probe_id)
            )

        deleted_probe = await self.query_db(query.returning(mProbe.c.name))

        if deleted_probe is None:
            error = "That probe doesn't exist anymore."
            return json_response({"error": error}, status=400)

        await Spawner.probe.delete(name=deleted_probe.name)
        event = {
            "user_id": user_id,
            "name": deleted_probe.name,
        }
        await streaming.publish("service.probe.deleted", event)
        message = f"We are removing {deleted_probe.name}"
        return json_response({"message": message})
