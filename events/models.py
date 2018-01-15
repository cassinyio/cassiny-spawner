"""
Logs models.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from factory import metadata

mLog = Table(
    'logs',
    metadata,
    Column('id', Integer, primary_key=True),
    # unique log identifier
    Column('uuid', UUID()),
    Column('log_type', String(10)),
    Column('service_type', String(5)),
    Column('name', String(200)),
    Column('action', String(10)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('user_id', Integer, nullable=False),

    # uuid-action should be unique
    UniqueConstraint('uuid', 'action'),
)
