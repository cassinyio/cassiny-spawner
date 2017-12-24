"""
APIs models.

Copyright (c) 2017, Cassiny.io OÜ
All rights reserved.
"""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Unicode,
)
from sqlalchemy.sql import func

from factory import metadata

mApi = Table(
    'apis',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100), unique=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('specs', JSON),
    Column('description', Unicode(255)),
    Column('active', Boolean, default=False),
    Column('user_id', Integer, nullable=False),
    Column('blueprint_id', Integer, ForeignKey("blueprints.id"),
           nullable=False),
)
