"""
Jobs views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging

from aiohttp.web import json_response
from rampante import streaming
from sqlalchemy.sql import select

from blueprints.models import mBlueprint
from cargos.models import mCargo
from jobs.models import mJob
from jobs.serializers import JobSchema
from utils import WebView, check_quota, verify_token

log = logging.getLogger(__name__)


class Jobs(WebView):
    """List, get and create Jobs."""

    @verify_token
    async def get(self, payload):
        """Get a list of Jobs for the current user"""
        user_id = payload["user_id"]

        async with self.db.acquire() as conn:
            query = select([
                mJob,
                mCargo.c.name.label("cargo_name"),
                mBlueprint.c.name.label("blueprint_name"),
                mBlueprint.c.repository.label("blueprint_repository"),
            ])\
                .where(mJob.c.user_id == user_id)\
                .select_from(
                    mJob
                    .outerjoin(mCargo, mJob.c.cargo_id == mCargo.c.id)
                    .outerjoin(mBlueprint, mJob.c.blueprint_id == mBlueprint.c.id)
            )

            result = await conn.execute(query)
            jobs = await result.fetchall()

        job_schema = JobSchema(many=True)
        job_schema.context = {"user": user_id}
        data, errors = job_schema.dump(jobs)

        if errors:
            log.warning(
                f"Error while handling request from user {user_id} request: {errors}")
            return json_response(errors, status=400)

        body = {"jobs": data}
        return json_response(body)

    @verify_token
    @check_quota(mJob)
    async def post(self, payload):
        """Create a new job."""
        user_id = payload["user_id"]
        data = await self.request.json()

        data, errors = JobSchema().load(data)

        if errors:
            log.warning(
                f"Error while handling request from user {user_id}: {errors}")
            body = {"message": errors}
            return json_response(body, status=400)

        # Create the new jobs
        event = {
            "user_id": user_id,
            "specs": data
        }

        await streaming.publish("service.probe.create", event)

        message = "We are creating your job......."
        return json_response({"message": message})

    @verify_token
    async def delete(self, payload):
        """Delete Job endpoint given and id."""
        user_id = payload["user_id"]
        # get the job_id from the url path
        job_id = self.request.match_info.get("job_id")

        log.info(f"Request to delete Job '{job_id}' from user '{user_id}'")

        async with self.db.acquire() as conn:
            query = mJob.delete().where(
                (mJob.c.user_id == user_id) &
                (mJob.c.id == job_id)
            ).returning(
                mJob.c.name
            )
            result = await conn.execute(query)
            # returns None if job_id doesn't exist
            deleted_job = await result.fetchone()

        # Delete the job
        if deleted_job is not None:
            event = {
                "user_id": user_id,
                "name": deleted_job.name,
            }

            await streaming.publish("service.probe.delete", event)

            user_message = f"We are removing {deleted_job.name}"
            body = {"message": user_message}
            return json_response(body)

        message = f"User has tried to remove a job that doesn't exist inside the database: {job_id}"
        log.error(message)
        user_message = f"It seems that job doesn't exist anymore"
        body = {"message": user_message}
        return json_response(body)
