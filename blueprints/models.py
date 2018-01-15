"""
Blueprints models.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Table,
)
from sqlalchemy.sql import func

from factory import metadata

mBlueprint = Table(
    'blueprints',
    metadata,
    Column('id', Integer, primary_key=True),
    # repository is composed with the registry name also
    Column('repository', String(100)),
    Column('name', String(50)),
    Column('tag', String(10)),
    Column('link', String(255), nullable=True),
    Column('description', String(255)),
    Column('public', Boolean, default=False),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('user_id', Integer, nullable=True),

)
