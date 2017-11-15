import logging
import logging.config

from sqlalchemy import create_engine

from apis.models import mApi
from blueprints.models import mBlueprint
from cargos.models import mCargo
from jobs.models import mJob
from probes.models import mProbe
from config import Config as C
from factory import metadata


logging.config.dictConfig(C.DEFAULT_LOGGING)
log = logging.getLogger(__name__)


def create_tables():
    """Create db tables."""
    dsn = f"postgresql+psycopg2://{C.DB_USER}:{C.DB_PASSWORD}@{C.DB_HOST}/{C.DB_NAME}"
    try:
        engine = create_engine(dsn)
        metadata.create_all(engine)
        log.info("Tables created")
    except Exception:
        log.exception("Something went wrong")
        raise


if __name__ == "__main__":
    create_tables()
