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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func

from factory import metadata

mProbe = Table(
    'probes', metadata,
    Column('uuid', UUID, primary_key=True),
    Column('name', String(100), unique=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('description', Unicode(255)),
    Column('specs', JSONB),
    Column('token', String(45)),
    Column('status', Integer, default=0),

    Column('user_id', Integer, nullable=False),
    Column('blueprint_uuid', UUID, ForeignKey("blueprints.uuid"),
           nullable=False),
)


mUser_probes = Table(
    'user_probes', metadata,
    Column('id', Integer, primary_key=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('probe_uuid', UUID, ForeignKey("probes.uuid"), nullable=False),
    Column('user_id', Integer, nullable=False),
)


async def delete_probe(db, probe_ref: str, user_id: str):
    """Remove a probe from the database."""
    query = mProbe.delete().where(
        (
            mProbe.c.user_id == user_id) &
        (
            mProbe.c.uuid == probe_ref |
            mProbe.c.name == probe_ref
        )
    )
    async with db.acquire() as conn:
        result = await conn.execute(query.returning(mProbe.c.name))
        row = await result.fetchone()
    return row
