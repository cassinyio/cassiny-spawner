"""
APIs models.

Copyright (c) 2017, Cassiny.io OÜ
All rights reserved.
"""

import uuid

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Unicode,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from factory import metadata

mApi = Table(
    'apis',
    metadata,
    Column('uuid', UUID, primary_key=True),
    Column('name', String(100), unique=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('specs', JSONB),
    Column('description', Unicode(255)),
    Column('status', Integer, default=0),

    Column('user_id', Integer, nullable=False),
    Column('blueprint_uuid', UUID, ForeignKey("blueprints.uuid"),
           nullable=False),
)


async def delete_api(db, api_ref: str, user_id: str):
    """Remove an api from the database."""
    # check if cargo_uuid is a valid uuid
    # if not we consider it a name
    try:
        uuid.UUID(api_ref)
    except ValueError:
        query = mApi.delete()\
            .where(
            (mApi.c.user_id == user_id) &
            (mApi.c.name == api_ref)
        )
    else:
        query = mApi.delete()\
            .where(
            (mApi.c.user_id == user_id) &
            (mApi.c.uuid == api_ref)
        )
    async with db.acquire() as conn:
        result = await conn.execute(query.returning(mApi.c.name))
        row = await result.fetchone()
    return row
