"""
Cargos models.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from factory import metadata

mCargo = Table(
    'cargos', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True),
    Column('specs', JSONB),
    Column('status', Integer, default=0),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('user_id', Integer, nullable=False),
)

mUser_cargos = Table(
    'user_cargos', metadata,
    Column('id', Integer, primary_key=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('user_id', Integer, nullable=False),
    Column('cargo_id', Integer, ForeignKey(
        "cargos.id"), nullable=False),
)
