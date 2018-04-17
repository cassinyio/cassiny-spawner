"""
Jobs models.

:copyright: (c) 2017, Cassiny.io OÜ.
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
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, select

from factory import metadata

mJob = Table(
    'jobs', metadata,
    Column('uuid', UUID, primary_key=True),
    Column('name', String(100), unique=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('deleted_at', DateTime(timezone=True),
           nullable=True),
    Column('specs', JSONB),
    Column('description', String(255)),
    Column('status', Integer, default=0),
    Column('user_id', Integer, nullable=False),
    Column('blueprint_uuid', UUID,
           ForeignKey("blueprints.uuid"), nullable=False),
)


async def update_job_status(db, job_ref: str, user_id: str):
    """Remove a job from the database."""
    try:
        uuid.UUID(job_ref)
    except ValueError:
        query = mJob.update()\
            .where(
            (mJob.c.user_id == user_id) &
            (mJob.c.name == job_ref)
        )
    else:
        query = mJob.update()\
            .where(
            (mJob.c.user_id == user_id) &
            (mJob.c.uuid == job_ref)
        )

    async with db.acquire() as conn:
        result = await conn.execute(query.values(deleted_at=func.now())
                                    .returning(mJob.c.uuid, mJob.c.name))
        row = await result.fetchone()
    return row


async def update_job_status_with_uuid(db, job_uuid: str) -> None:
    """Remove a job from the database."""

    query = mJob.update().where(mJob.c.uuid == job_uuid).values(deleted_at=func.now())

    async with db.acquire() as conn:
        await conn.execute(query)


async def select_job(db, job_ref: str, user_id: str):
    """Select an api from the database."""
    try:
        uuid.UUID(job_ref)
    except ValueError:
        query = select([
            mJob
        ]).where(
            (mJob.c.user_id == user_id) &
            (mJob.c.name == job_ref)
        )
    else:
        query = select([
            mJob
        ]).where(
            (mJob.c.user_id == user_id) &
            (mJob.c.uuid == job_ref)
        )
    async with db.acquire() as conn:
        result = await conn.execute(query)
        row = await result.fetchone()
    return row
