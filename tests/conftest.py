# content of conftest.py
import asyncio
import logging
import logging.config

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiopg.sa import create_engine as aiopg_create_engine
from psycopg2 import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.schema import CreateTable
from sqlalchemy_utils.functions import (
    create_database,
    database_exists,
    drop_database,
)

from apis import mApi
from apis import routes as api_routes
from app import (
    add_route,
    start_task_manager,
    stop_db_pool,
    stop_task_manager,
)
from blueprints import mBlueprint
from blueprints import routes as blueprint_routes
from cargos import mCargo, mUser_cargos
from cargos import routes as cargo_routes
from config import Config as C
from monitoring import mLog, routes as monitoring_routes
from jobs import mJob
from jobs import routes as job_routes
from probes import mProbe, mUser_probes
from probes import routes as probe_routes
from tests.fixtures import _validate_token

logging.config.dictConfig(C.DEFAULT_LOGGING)
log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def create_tables():
    """Create all the tables needed for the test."""
    DB_URI = f'postgresql://{C.DB_USER}:{C.DB_PASSWORD}@{C.DB_HOST}:{C.DB_PORT}/{C.DB_NAME}'
    if database_exists(DB_URI):
        drop_database(DB_URI)
    create_database(DB_URI)
    engine = create_engine(DB_URI)

    conn = engine.connect()
    models = [mBlueprint, mCargo, mApi, mProbe,
              mUser_probes, mJob, mUser_cargos, mLog]
    for model in models:
        conn.execute(CreateTable(model).compile(engine).__str__())
    add_blueprint = """INSERT INTO "public"."blueprints"("uuid","repository","name","tag","link","description","public","created_at","user_id")
    VALUES('2a83d4be0f7011e89e4b35694e577c22','cassinyio','notebook','02946e48',NULL,NULL,TRUE,E'2017-12-16 22:46:13.515348+00',NULL);"""
    conn.execute(add_blueprint)


@pytest.fixture(scope="session")
def loop():
    """Factory to create a TestClient instance.
    test_client(app, **kwargs)
    test_client(server, **kwargs)
    test_client(raw_server, **kwargs)
    """

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop

    # Clean-up
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def test_client(loop):
    """Factory to create a TestClient instance.
    test_client(app, **kwargs)
    test_client(server, **kwargs)
    test_client(raw_server, **kwargs)
    """
    clients = []

    async def go(__param, *args, server_kwargs=None, **kwargs):

        server_kwargs = server_kwargs or {}
        server = TestServer(__param, loop=loop, **server_kwargs)
        client = TestClient(server, loop=loop, **kwargs)

        await client.start_server()
        clients.append(client)
        return client

    yield go

    async def finalize():
        while clients:
            await clients.pop().close()

    loop.run_until_complete(finalize())


async def start_db_pool(app):
    """Create a db pool."""
    # Database engine is shared among the requests
    try:
        engine = await aiopg_create_engine(
            user=C.DB_USER,
            password=C.DB_PASSWORD,
            database=C.DB_NAME,
            host=C.DB_HOST,
            port=C.DB_PORT,
        )
    except OperationalError as err:
        log.error("Are you sure that POSTGRE is working?")
        raise err
    app["db"] = engine


@pytest.fixture(scope="session")
def cli(loop, test_client, create_tables):
    app = web.Application(loop=loop)
    add_route(
        app,
        *api_routes,
        *blueprint_routes,
        *job_routes,
        *probe_routes,
        *cargo_routes,
        *monitoring_routes,
    )
    app.on_startup.append(start_task_manager)
    app.on_startup.append(start_db_pool)

    app.on_cleanup.append(stop_task_manager)
    app.on_cleanup.append(stop_db_pool)
    return loop.run_until_complete(test_client(app))


@pytest.fixture
def valid_token(monkeypatch):
    """Patch `utils.auth._validate_token` passing fake token."""
    monkeypatch.setattr('utils.auth._validate_token', _validate_token)
    yield
    monkeypatch.undo()
