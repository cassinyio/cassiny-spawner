"""
Jobs models.

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

mJob = Table(
    'jobs', metadata,
    Column('uuid', UUID(), primary_key=True),
    Column('name', String(100), unique=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('specs', JSONB),
    Column('description', Unicode(255)),
    Column('status', Integer, default=0),
    Column('user_id', Integer, nullable=False),
    Column('blueprint_id', Integer,
           ForeignKey("blueprints.id"), nullable=False),
)


async def delete_job(db, job_ref: str, user_id: str):
    """Remove a job from the database."""
    query = mJob.delete().where(
        (
            mJob.c.user_id == user_id) &
        (
            mJob.c.uuid == job_ref |
            mJob.c.name == job_ref
        )
    )
    async with db.acquire() as conn:
        result = await conn.execute(query.returning(mJob.c.name))
        row = await result.fetchone()
    return row
