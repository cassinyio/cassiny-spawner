"""
    models.py
    ~~~~~~~~~
    APIs models

    :copyright: (c) 2017, Cassiny.io OÜ.
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
    'apis', metadata,

    Column('id', Integer, primary_key=True),

    # name and subdomain of the service
    Column('name', String(100), unique=True),

    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('specs', JSON),

    Column('description', Unicode(255)),

    # if the service is running or not
    Column('active', Boolean, default=False),

    # Creator of the Container
    Column('user_id', Integer, nullable=False),

    Column('blueprint_id', Integer, ForeignKey("blueprints.id"),
           nullable=False),

    Column('cargo_id', Integer,
           ForeignKey("cargos.id"), nullable=True),
)
