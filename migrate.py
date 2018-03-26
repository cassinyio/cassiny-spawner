import logging
import logging.config

from alembic.config import Config as AlembicConfig
from alembic import command

from auth import models  # noqa: F401
from config import Config

logging.config.dictConfig(Config.DEFAULT_LOGGING)
log = logging.getLogger(__name__)


def make_migration():
    """Migrate database"""
    try:
        log.info("Migrating cassiny-spawner's db tables.")
        alembic_cfg = AlembicConfig("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception:
        log.exception("Something went wrong during cassiny-spawner's db tables migration.")
        raise


if __name__ == "__main__":
    make_migration()
