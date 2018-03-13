import asyncio
import logging
from types import MappingProxyType

from rampante import streaming
from sqlalchemy.exc import IntegrityError

from apis import mApi
from cargos import mCargo
from events.service import (
    add_log,
    prepare_message,
    update_service_status,
    validate_docker_event,
)
from jobs import mJob
from probes import mProbe

MODEL_TYPE = MappingProxyType({
    "probe": mProbe,
    "api": mApi,
    "cargo": mCargo,
    "job": mJob,
})


log = logging.getLogger(__name__)

TOPIC_NAME = 'user.notification'


async def docker_listener(app):
    """Docker events listener."""
    log.info("docker watcher started")
    subscriber = app['docker'].events.subscribe()
    try:
        while True:
            event = await subscriber.get()

            if event is None:
                break

            with validate_docker_event(event) as dockerlog:

                if dockerlog:

                    log.info(dockerlog.to_dict())

                    model = MODEL_TYPE[dockerlog.service_type]

                    try:
                        await add_log(app['db'], dockerlog)
                    except IntegrityError:
                        # The paig log uuid and action is already inside the db
                        log.warning(f"Log ID ({dockerlog.uuid}) with action ({dockerlog.action}) is already inside the db, skipping.")
                    else:
                        await update_service_status(app['db'], model, dockerlog)

                    message = prepare_message(dockerlog)
                    if message:
                        await streaming.publish(TOPIC_NAME, message)

    except asyncio.CancelledError:
        log.info("Shutting down docker watcher....")
