"""
Logs models.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import re
from typing import Dict

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
from utils import query_db

REGEX = re.compile('([a-z]+)-[a-z]+-[0-9]{4}$')

mLog = Table(
    'logs',
    metadata,
    Column('id', Integer, primary_key=True),
    # unique log identifier
    Column('uuid', UUID),
    Column('log_type', String(10)),
    Column('service_type', String(5)),
    Column('name', String(200)),
    Column('action', String(10)),
    Column('created_at', DateTime, server_default=func.now()),
    Column('user_id', Integer, nullable=False),

    # uuid-action should be unique
    UniqueConstraint('uuid', 'action'),
)


async def add_log(db, event: Dict) -> None:
    """Add a new log for services events."""
    query = mLog.insert().values(
        uuid=event['uuid'],
        log_type=event['type'],
        service_type=event['service_type'],
        name=event['name'],
        action=event['action'],
        user_id=event['user_id']
    )
    await query_db(db, query, get_result=False)


async def update_service_status(db, model, event) -> None:
    """Update status for a docker event."""
    if "status" in event and event['status']:
        query = model.update()\
            .where(model.c.name == event.name)\
            .values(
            status=event['status'],
        )
        await query_db(db, query, get_result=False)
