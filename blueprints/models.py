"""
Blueprints models.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, select
from sqlalchemy.exc import IntegrityError

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

    # each image should be unique
    UniqueConstraint('repository', 'name', 'tag'),
)


async def join_blueprints_with(model, user_id: str, db):
    query = select([
        model,
        mBlueprint.c.name.label("blueprint_name"),
        mBlueprint.c.repository.label("blueprint_repository"),
        mBlueprint.c.tag.label("blueprint_tag"),
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


async def get_blueprint(db, blueprint_ref: str, user_id: str):
    try:
        uuid.UUID(blueprint_ref)
    except ValueError:
        # blueprint_ref is not a uuid
        blueprint_data = blueprint_ref.split("/")
        tag = "latest"

        if len(blueprint_data) == 2:
            repository, name = blueprint_data

            name_data = name.split(":")
            if len(name_data) == 2:
                name, tag = name_data

        elif len(blueprint_data) == 3:
            repository = "/".join(blueprint_data[:2])
            name = blueprint_data[-1]

            name_data = name.split(":")
            if len(name_data) == 2:
                name, tag = name_data

        else:
            return None

        query = mBlueprint.select().where(
            (
                (mBlueprint.c.repository == repository) &
                (mBlueprint.c.name == name) &
                (mBlueprint.c.tag == tag)
            ) &
            (
                (mBlueprint.c.user_id == user_id) |
                (mBlueprint.c.public.is_(True))
            )
        )
    else:
        query = mBlueprint.select().where(
            (mBlueprint.c.uuid == blueprint_ref) &
            (
                (mBlueprint.c.user_id == user_id) |
                (mBlueprint.c.public.is_(True))
            )
        )

    async with db.acquire() as conn:
        result = await conn.execute(query)
        row = await result.fetchone()
    return row


async def get_your_blueprint(db, blueprint_ref: str, user_id: str):
    """Get the blueprint only if you are the owner."""
    try:
        uuid.UUID(blueprint_ref)
    except ValueError:
        # blueprint_ref is not a uuid
        blueprint_data = blueprint_ref.split("/")
        tag = "latest"

        if len(blueprint_data) == 2:
            repository, name = blueprint_data

            name_data = name.split(":")
            if len(name_data) == 2:
                name, tag = name_data

        elif len(blueprint_data) == 3:
            repository = "/".join(blueprint_data[:2])
            name = blueprint_data[-1]

            name_data = name.split(":")
            if len(name_data) == 2:
                name, tag = name_data

        else:
            return None

        query = mBlueprint.select().where(
            (
                (mBlueprint.c.repository == repository) &
                (mBlueprint.c.name == name) &
                (mBlueprint.c.tag == tag)
            ) &
            (
                mBlueprint.c.user_id == user_id
            )
        )
    else:
        query = mBlueprint.select().where(
            (mBlueprint.c.uuid == blueprint_ref) &
            (
                mBlueprint.c.user_id == user_id
            )
        )

    async with db.acquire() as conn:
        result = await conn.execute(query)
        row = await result.fetchone()
    return row


async def delete_blueprint(db, blueprint_ref: str, user_id: str):
    """Remove a blueprint from the database."""
    blueprint = await get_your_blueprint(db, blueprint_ref, user_id)
    if blueprint:
        query = mBlueprint.delete().where(mBlueprint.c.uuid == blueprint.uuid)
        async with db.acquire() as conn:
            await conn.execute(query)
        return blueprint
    return None


async def upsert_blueprint(
    db,
    uuid: str,
    repository: str,
    user_id: str,
    name: str,
    tag: str,
    description: str
):
    """Insert or update a blueprint."""
    query = mBlueprint.insert().values(
        uuid=uuid,
        repository=repository,
        name=name,
        tag=tag,
        user_id=user_id,
        description=description
    )

    try:
        async with db.acquire() as conn:
            await conn.execute(query)
    except IntegrityError:
        query = mBlueprint.update()\
            .where(
            (mBlueprint.c.repository == repository) &
            (mBlueprint.c.name == name) &
            (mBlueprint.c.tag == tag)
        )\
            .values(
            uuid=uuid,
            description=description,
            deleted_at=func.now()
        )

        async with db.acquire() as conn:
            await conn.execute(query)
