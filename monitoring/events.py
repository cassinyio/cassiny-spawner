"""Monitoring docker's events."""

import logging
from types import MappingProxyType

from rampante import subscribe_on
from sqlalchemy.exc import IntegrityError

from apis import mApi
from cargos import mCargo
from jobs.helpers import delete_a_job
from jobs.models import mJob, update_job_status_with_uuid
from monitoring.models import add_log, update_service_status
from probes import mProbe

log = logging.getLogger(__name__)

MODEL_TYPE = MappingProxyType({
    "probe": mProbe,
    "api": mApi,
    "cargo": mCargo,
    "job": mJob,
})


@subscribe_on("service.notification")
async def service_notification(queue, event, app):
    """Save service notifications."""
    log.info(f"Container event received: {event}")

    model = MODEL_TYPE.get(event['service_type'])

    if model is None:
        log.error(f"Invalid service type {event['service_type']}")
        return

    # remove a job after exited
    if event['service_type'] == 'job' and event['action'] == 'die':
        log.info(f"Removing job({event['uuid']}) with name {event['name']} after exited.")
        update_job_status_with_uuid(app['db'], event['uuid'])
        await delete_a_job(event['uuid'], event['name'], event['user_id'])

    try:
        await add_log(app['db'], event)
    except IntegrityError:
        # the log uuid and action is already inside the db
        log.warning(f"Log ID ({event['uuid']}) with action ({event['action']}) is already inside the db, skipping.")
    else:
        await update_service_status(app['db'], model, event)
