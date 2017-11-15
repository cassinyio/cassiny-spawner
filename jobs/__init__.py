"""Jobs endpoints."""

from jobs.routes import routes
from jobs.models import mJob

__all__ = ("routes", "mJob")
