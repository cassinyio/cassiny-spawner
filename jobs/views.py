"""
Jobs views.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import logging
from typing import Any, Mapping

from aiohttp.web import json_response
from rampante import streaming

from blueprints.models import join_blueprints_with
from jobs.models import delete_job, mJob, select_job
from jobs.serializers import JobSchema
from spawner import Spawner
from utils import WebView, get_uuid, verify_token

log = logging.getLogger(__name__)


class Jobs(WebView):
    """List, get and create Jobs."""

    @verify_token
    async def get(self, payload: Mapping[str, Any]):
        """Get a list of Jobs for the current user"""
        user_id = payload["user_id"]

        jobs = await join_blueprints_with(model=mJob, db=self.db, user_id=user_id)
        job_schema = JobSchema(many=True)
        job_schema.context = {"user": user_id}

        data, errors = job_schema.dump(jobs)

        if errors:
            return json_response({"error": errors}, status=400)

        return json_response({"jobs": data})

    @verify_token
    async def post(self, payload: Mapping[str, Any]):
        """Create a new job."""
        user_id = payload['user_id']
        data = await self.request.json()

        data, errors = JobSchema().load(data)
        if errors:
            log.debug(errors)
            return json_response({"error": errors}, status=400)

        event = {
            "uuid": get_uuid().hex,
            "user_id": user_id,
            "data": data
        }

        await streaming.publish("service.job.create", event)

        return json_response({"message": f"We are creating your job ({event['uuid']})."})

    @verify_token
    async def delete(self, payload: Mapping[str, Any]):
        """Delete a job."""
        user_id = payload["user_id"]
        job_ref = self.request.match_info.get("job_ref")

        deleted_job = await delete_job(self.db, job_ref=job_ref, user_id=user_id)

        if deleted_job is None:
            error = "That job doesn't exist anymore."
            return json_response({"error": error}, status=400)

        await Spawner.job.delete(name=deleted_job.name)

        event = {
            "user_id": user_id,
            "name": deleted_job.name,
        }

        await streaming.publish("service.job.deleted", event)
        user_message = f"Job {deleted_job.name} removed."
        return json_response({"message": user_message})


class Logs(WebView):
    """Views to get job Logs."""

    @verify_token
    async def get(self, payload):
        user_id = payload["user_id"]
        job_ref = self.request.match_info.get("job_ref")

        selected_job = await select_job(db=self.db, job_ref=job_ref, user_id=user_id)

        if selected_job is None:
            user_message = f"It seems that probe doesn't exist anymore."
            return json_response({"error": user_message}, status=400)

        logs = await Spawner.job.logs(name=selected_job.name)
        return json_response({"logs": logs})
