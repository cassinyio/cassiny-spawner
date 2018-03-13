"""
Probes views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming

from blueprints.models import join_blueprints_with
from probes.models import delete_probe, mProbe
from probes.serializers import ProbeSchema
from spawner import Spawner
from utils import WebView, get_uuid, verify_token

log = logging.getLogger(__name__)

type_payload = Mapping[str, Any]


class Probe(WebView):
    """Get info, create and remove probes."""

    @verify_token
    async def get(self, payload: type_payload):
        """Get probes."""
        user_id = payload['user_id']

        probes = await join_blueprints_with(model=mProbe, db=self.db, user_id=user_id)
        probes_schema = ProbeSchema(many=True)
        probes_schema.context = {"user": user_id}

        data, errors = probes_schema.dump(probes)

        if errors:
            return json_response({"error": errors}, status=400)

        return json_response({"probes": data})

    @verify_token
    async def post(self, payload: type_payload):
        """Create new probes."""
        user_id = payload["user_id"]
        data = await self.request.json()

        data, errors = ProbeSchema().load(data)
        if errors:
            return json_response({"error": errors}, status=400)

        event = {
            "uuid": get_uuid().hex,
            "user_id": user_id,
            "data": data
        }

        await streaming.publish("service.probe.create", event)
        log.info(f"{event['uuid']}: {event}")

        return json_response({"message": "We are creating your Job."})

    @verify_token
    async def delete(self, payload: type_payload):
        """Delete probes."""
        probe_ref = self.request.match_info.get("probe_ref")
        user_id = payload['user_id']

        deleted_probe = await delete_probe(self.db, probe_ref=probe_ref, user_id=user_id)

        if deleted_probe is None:
            error = "That probe doesn't exist anymore."
            return json_response({"error": error}, status=400)

        await Spawner.probe.delete(name=deleted_probe.name)
        event = {
            "user_id": user_id,
            "name": deleted_probe.name,
        }
        await streaming.publish("service.probe.deleted", event)
        message = f"Probe {deleted_probe.name} removed."
        return json_response({"message": message})
