"""
Jobs views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.exc import InterfaceError, InternalError
from sqlalchemy.sql import select, update

from blueprints.models import mBlueprint
from config import Config as C
from jobs.models import mJob
from jobs.serializers import JobSchema
from spawner import Spawner
from utils import (
    WebView,
    check_quota,
    naminator,
    verify_token,
)

log = logging.getLogger(__name__)


class Jobs(WebView):
    """List, get and create Jobs."""

    @verify_token
    async def get(self, payload: Mapping[str, Any]):
        """Get a list of Jobs for the current user"""
        user_id = payload["user_id"]

        async with self.db.acquire() as conn:
            query = select([
                mJob,
                mBlueprint.c.name.label("blueprint_name"),
                mBlueprint.c.repository.label("blueprint_repository"),
            ])\
                .where(mJob.c.user_id == user_id)\
                .select_from(
                    mJob
                    .outerjoin(mBlueprint, mJob.c.blueprint_id == mBlueprint.c.id)
            )

            result = await conn.execute(query)
            jobs = await result.fetchall()

        job_schema = JobSchema(many=True)
        job_schema.context = {"user": user_id}
        data, errors = job_schema.dump(jobs)

        if errors:
            return json_response({"error": errors}, status=400)

        body = {"jobs": data}
        return json_response(body)

    @verify_token
    @check_quota(mJob)
    async def post(self, payload: Mapping[str, Any]):
        """Create a new job."""
        user_id = payload["user_id"]
        data = await self.request.json()

        data, errors = JobSchema().load(data)
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
            error = "Did you select the right blueprint?"
            return json_response({"error": error}, status=400)

        cpu, ram, gpu = C.SIZE[data['machine_type']]

        specs = {
            'repository': blueprint.repository,
            'blueprint': f"{blueprint.name}:{blueprint.tag}",
            'machine_type': data['machine_type'],
            'command': data['command'],
            'cpu': cpu,
            'ram': ram,
            'gpu': gpu,
        }

        name = naminator("job")

        try:
            query = mJob.insert().values(
                user_id=user_id,
                blueprint_id=blueprint.id,
                name=name,
                description=data['description'],
                specs=specs,
            )
            await self.query_db(query, get_result=False)
        except InterfaceError:
            return json_response({"error": errors}, status=400)

        service = await Spawner.job.create(
            name=name,
            user_id=user_id,
            specs=specs,
        )

        if not service:
            try:
                query = update(mJob).where(
                    mJob.c.name == name).values(status=3)
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
        """Delete a job."""
        user_id = payload["user_id"]
        job_id = self.request.match_info.get("job_id")

        try:
            query = mJob.delete()\
                .where(
                (mJob.c.user_id == user_id) &
                (mJob.c.id == int(job_id))
            )
        except ValueError:
            query = mJob.delete()\
                .where(
                (mJob.c.user_id == user_id) &
                (mJob.c.name == job_id)
            )

        async with self.db.acquire() as conn:
            result = await conn.execute(query.returning(mJob.c.name))
            deleted_job = await result.fetchone()

        if deleted_job is None:
            error = "That job doesn't exist anymore."
            return json_response({"error": error}, status=400)

        result = await Spawner.job.delete(name=deleted_job.name)
        event = {
            "user_id": user_id,
            "name": deleted_job.name,
        }
        await streaming.publish("service.probe.deleted", event)
        user_message = f"We are removing {deleted_job.name}"
        return json_response({"message": user_message})
