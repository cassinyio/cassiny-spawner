"""
Launcher for mcc.cassiny.io.

Copyright (c) 2017, Cassiny.io OÜ
All rights reserved.
"""

import asyncio
import logging
import logging.config
import sys

from aiohttp import web
from aiopg.sa import create_engine
from psycopg2 import OperationalError
from rampante import scheduler, streaming

from apis import routes as api_routes
from blueprints import routes as blueprint_routes
from cargos import routes as cargo_routes
from config import Config as C
from jobs import routes as job_routes
from probes import routes as probe_routes

logging.config.dictConfig(C.DEFAULT_LOGGING)
log = logging.getLogger(__name__)


def add_route(app, *args):
    """
    Add routes to app instance.
    :app: instance of the app
    """
    for route in args:
        app.router.add_route(route[0], route[1], route[2])


async def start_db_pool(app):
    """Load a background task executor."""
    # Database engine is shared among the requests
    try:
        engine = await create_engine(
            user=C.DB_USER,
            password=C.DB_PASSWORD,
            database=C.DB_NAME,
            host=C.DB_HOST,
        )
    except OperationalError as err:
        log.error("Are you sure that POSTGRE SQL is working?")
        raise err
    app["db"] = engine


async def stop_db_pool(app):
    """Cancel db pool."""
    if 'db' in app:
        app['db'].close()
        await app["db"].wait_closed()


async def start_task_manager(app):
    """Connect to the streams."""
    await streaming.start(server=C.STREAM_URI, client_name="service-01", service_group="service-spawner", loop=app.loop)
    app['task_manager'] = asyncio.ensure_future(
        scheduler(loop=app.loop, queue_size=50))


async def stop_task_manager(app):
    """Cancel task manager."""
    await streaming.stop()
    if 'task_manager' in app:
        app['task_manager'].cancel()
        await app['task_manager']


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    app = web.Application()
    add_route(
        app,
        *api_routes,
        *blueprint_routes,
        *job_routes,
        *probe_routes,
        *cargo_routes,
    )

    # On-startup tasks
    app.on_startup.append(start_task_manager)
    app.on_startup.append(start_db_pool)
    # Clean-up tasks
    app.on_cleanup.append(stop_task_manager)
    app.on_cleanup.append(stop_db_pool)

    web.run_app(app, host=host, port=port)
