"""
Probes models.

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
    Unicode,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from factory import metadata

mProbe = Table(
    'probes', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('description', Unicode(255)),
    Column('specs', JSONB),
    Column('token', String(45)),
    Column('status', Integer, default=0),

    Column('user_id', Integer, nullable=False),
    Column('blueprint_id', Integer, ForeignKey("blueprints.id"),
           nullable=False),
)


mUser_probes = Table(
    'user_probes', metadata,
    Column('id', Integer, primary_key=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('probe_id', Integer, ForeignKey("probes.id"), nullable=False),
    Column('user_id', Integer, nullable=False),
)
