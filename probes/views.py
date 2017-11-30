"""
    views.py
    ~~~~~~~~~
    Probes views

    :copyright: (c) 2017, Cassiny.io OÜ.
    All rights reserved.
"""

import logging
from uuid import uuid4

import msgpack
from aiohttp.web import json_response
from psycopg2 import DataError
from rampante import streaming
from sqlalchemy.sql import select

from blueprints.models import mBlueprint
from cargos.models import mCargo
from probes.models import mProbe
from probes.serializers import ProbeSchema
from utils import WebView, naminator, verify_token

log = logging.getLogger(__name__)


class Probe(WebView):
    """
    Used to get info, create and remove probes
    """

    @verify_token
    async def get(self, user_id):
        """Get info about a probe."""

        async with self.db.acquire() as conn:
            query = select([
                mProbe,
                mCargo.c.name.label("cargo_name"),
                mBlueprint.c.name.label("blueprint_name"),
                mBlueprint.c.repository.label("blueprint_repository"),
            ])\
                .where(mProbe.c.user_id == user_id)\
                .select_from(
                mProbe
                .outerjoin(mCargo, mProbe.c.cargo_id == mCargo.c.id)
                .outerjoin(mBlueprint, mProbe.c.blueprint_id == mBlueprint.c.id)
            )
            result = await conn.execute(query)
            probes = await result.fetchall()

        probes_schema = ProbeSchema(
            many=True,
            exclude=('subdomain')
        )
        probes_schema.context = {"user": user_id}
        data, errors = probes_schema.dump(probes)

        log.debug(f"Probe schema: {data}")

        if errors:
            log.warning(
                f"Error while handling request from user {user_id} request: {errors}")
            return json_response(errors, status=400)

        body = {"probes": data}
        return json_response(body)

    @verify_token
    async def post(self, user_id: int):
        """View to control the creation of probes."""
        data = await self.request.json()
        log.info(f"Data inside post request: {data}")

        data, errors = ProbeSchema().load(data)

        if errors:
            log.warning(f"Error while serializing: {errors} from {data}")
            message = "A field is missing :/"
            return json_response({"message": message}, status=400)

        # pick a random name for this probe
        name = naminator("probe")

        # Create the new jobs
        event = {
            "user_id": user_id,
            "name": name,
            "specs": data,
        }

        await streaming.publish("service.probe.create", event)

        message = f"We are preparing your probe {name}!"
        return json_response({"message": message})

    @verify_token
    async def patch(self, user_id):
        """
        Patch is for:
        - stop a probe without deleting it
        - update the allocated resources
        """

        # get the probe_ide from the url path
        probe_id = self.request.match_info.get("probe_id")

        log.info(f"Request to update probe: {probe_id}")

        data = await self.request.json()

        log.debug(data)

        # remove the route from both db/redis
        # but leave the record inside the probe model
        if "status" in data and data['status'] == "stop":
            try:
                async with self.db.acquire() as conn:
                    query = select([mProbe]).where(
                        (
                            (mProbe.c.user_id == user_id) &
                            (mProbe.c.id == probe_id)
                        )
                    )
                    result = await conn.execute(query)
                    # returns None if the probe doesn't exist
                    probe = await result.fetchone()

            except DataError:
                log.error(
                    f"Requested to delete probe: {probe_id}, "
                    f"but is an invalid name"
                )
                message = "Invalid `id` for a probe"
                body = {"message": message}
                return json_response(body, status=400)

            # delete the route from redis
            if probe:
                log.info(f"route {probe.name} deleted")

            event = {
                "user_id": user_id,
                "event_uuid": uuid4().hex,
                "name": probe.name,
                "specs": probe.specs
            }

            packed = msgpack.packb(event)
            print(packed)

            message = f"Probe {probe.name} removed"
            body = {"message": message}
            return json_response(body)

        # getting the route before deleting the probe
        # cause on cascade effect will delete also the route
        # TO COMPLETE
        if "status" in data and data['status'] == "update":
            async with self.db.acquire() as conn:
                query = select([mProbe]).where(
                    (
                        (mProbe.c.id == probe_id) &
                        (mProbe.c.user_id == user_id)
                    )
                )
            result = await conn.execute(query)

            # return None if the route doesn't exist
            probe = await result.fetchone()

            # update probe

            event = {
                "user_id": user_id,
                "event_uuid": uuid4().hex,
                "name": probe.name,
                "specs": probe.specs
            }

            packed = msgpack.packb(event)

            async with self.db.acquire() as conn:
                # update probe model
                query = mProbe.update()\
                    .where(
                        mProbe.c.id == probe.id
                )
            await conn.execute(query)

            message = f"Probe {probe.name} updated"
            body = {"message": message}
            return json_response(body)

        if "status" in data and data['status'] == "start":
            async with self.db.acquire() as conn:
                query = select([mProbe]).where(
                    (mProbe.c.id == probe_id) &
                    (mProbe.c.user_id == user_id)
                )
            result = await conn.execute(query)
            # return None if the route doesn't exist
            probe = await result.fetchone()

            # restart probe
            event = {
                "user_id": user_id,
                "event_uuid": uuid4().hex,
                "name": probe.name,
                "specs": probe.specs
            }

            packed = msgpack.packb(event)

            # internal url of the probe
            log.info(f"probe {probe.name} is reachable @ {probe.name}")

            message = f"Probe {probe.name} started!"
            body = {"message": message}
            return json_response(body)

    @verify_token
    async def delete(self, user_id):

        # get the probe_ide from the url path
        probe_id = self.request.match_info.get("probe_id")

        log.info(f"Request to delete probe: {probe_id}")

        try:

            async with self.db.acquire() as conn:
                # Deleted object
                query = mProbe.delete()\
                    .where(
                        (mProbe.c.user_id == user_id) &
                        (mProbe.c.id == probe_id)
                )\
                    .returning(
                        mProbe.c.name
                )
            result = await conn.execute(query)
            # returns None if probe_id doesn't exist
            deleted_probe = await result.fetchone()

        except DataError:
            log.error(
                f"Requested to delete probe: {probe_id}, "
                "but is an invalid name"
            )
            message = "probe_id needs to be a number"
            body = {"message": message, "result": "danger"}
            return json_response(body, status=400)

        if deleted_probe is None:
            log.error(
                f"Requested to delete probe: {probe_id}, "
                f"but it doesn't exist"
            )
            return json_response(
                {
                    "message": "mProbes doesn't exist",
                    "result": "danger"
                },
                status=200
            )

        # Create the new jobs
        event = {
            "user_id": user_id,
            "event_uuid": uuid4().hex,
            "name": deleted_probe.name,
        }

        packed = msgpack.packb(event)

        # emit event
        print(packed)

        message = f"We are removing your probe {deleted_probe.name}!"

        log.info(message)

        return json_response({"message": message})
