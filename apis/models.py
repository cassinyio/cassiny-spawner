"""
APIs models.

Copyright (c) 2017, Cassiny.io OÜ
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

mApi = Table(
    'apis',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('specs', JSONB),
    Column('description', Unicode(255)),
    Column('status', Integer, default=0),

    Column('user_id', Integer, nullable=False),
    Column('blueprint_id', Integer, ForeignKey("blueprints.id"),
           nullable=False),
)
