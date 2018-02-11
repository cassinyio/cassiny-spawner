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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, select

from factory import metadata

mBlueprint = Table(
    'blueprints',
    metadata,
    Column('uuid', UUID, primary_key=True),
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


async def join_blueprints_with(model, user_id: str, db):
    query = select([
        model,
        mBlueprint.c.name.label("blueprint_name"),
        mBlueprint.c.repository.label("blueprint_repository"),
    ])\
        .where(model.c.user_id == user_id)\
        .select_from(
        model
        .outerjoin(mBlueprint, model.c.blueprint_uuid == mBlueprint.c.uuid)
    )
    async with db.acquire() as conn:
        result = await conn.execute(query)
        rows = await result.fetchall()
    return rows


async def get_blueprints(db, user_id: str):
    query = mBlueprint.select().where(
        (mBlueprint.c.public.is_(True)) |
        (mBlueprint.c.user_id == user_id)
    )
    async with db.acquire() as conn:
        result = await conn.execute(query)
        rows = await result.fetchall()
    return rows


async def get_blueprint(db, blueprint_uuid: str, user_id: str):
    query = mBlueprint.select().where(
        (mBlueprint.c.uuid == blueprint_uuid) &
        (
            (mBlueprint.c.user_id == user_id) |
            (mBlueprint.c.public.is_(True))
        )
    )
    async with db.acquire() as conn:
        result = await conn.execute(query)
        row = await result.fetchone()
    return row
