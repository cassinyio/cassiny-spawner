"""Cargo package."""

from cargos.routes import routes
from cargos.models import mCargo, mUser_cargos

__all__ = ("routes", "mCargo", "mUser_cargos")
