import logging
import logging.config

from sqlalchemy import create_engine

import blueprints.models  # noqa
import cargos.models  # noqa
import jobs.models  # noqa
import probes.models  # noqa
from apis import mApi  # noqa
from config import Config
from events import mLog  # noqa
from factory import metadata

logging.config.dictConfig(Config.DEFAULT_LOGGING)
log = logging.getLogger(__name__)


def create_tables():
    """Create db tables."""
    try:
        engine = create_engine(Config.make_dsn())
        metadata.create_all(engine)
        log.info("cassiny-spawner's db tables created.")
    except Exception:
        log.exception("Something went wrong during cassiny-spawner's db tables creation.")
        raise


if __name__ == "__main__":
    create_tables()
