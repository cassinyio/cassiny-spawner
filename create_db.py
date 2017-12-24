import logging
import logging.config

from sqlalchemy import create_engine

import blueprints.models  # noqa
import cargos.models  # noqa
import jobs.models  # noqa
import probes.models  # noqa
from apis import mApi  # noqa
from config import Config as C
from events import mLog  # noqa
from factory import metadata

logging.config.dictConfig(C.DEFAULT_LOGGING)
log = logging.getLogger(__name__)


def create_tables():
    """Create db tables."""
    dsn = f"postgresql+psycopg2://{C.DB_USER}:{C.DB_PASSWORD}@{C.DB_HOST}:{C.DB_PORT}/{C.DB_NAME}"
    try:
        engine = create_engine(dsn)
        metadata.create_all(engine)
        log.info("Tables created")
    except Exception:
        log.exception("Something went wrong")
        raise


if __name__ == "__main__":
    create_tables()
