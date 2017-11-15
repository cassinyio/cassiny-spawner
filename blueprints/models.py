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
    Unicode,
)
from sqlalchemy.sql import func

from factory import metadata

mBlueprint = Table('blueprints', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('repository', String(100)),
                   Column('name', String(50)),
                   Column('tag', String(10)),
                   Column('dockerfile', String(255), nullable=True),
                   Column('link', String(255), nullable=True),
                   Column('description', Unicode(255)),
                   Column('public', Boolean, default=False),
                   Column('created_at', DateTime(timezone=True),
                          server_default=func.now()),
                   Column('user_id', Integer, nullable=True),
                   )
