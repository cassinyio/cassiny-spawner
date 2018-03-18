"""
Cargos models.

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
from sqlalchemy.sql import func

from factory import metadata

mCargo = Table(
    'cargos', metadata,
    Column('uuid', UUID, primary_key=True),
    Column('name', String(100), unique=True),
    Column('specs', JSONB),
    Column('status', Integer, default=0),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),

    Column('user_id', Integer, nullable=False),
)

mUser_cargos = Table(
    'user_cargos', metadata,
    Column('id', Integer, primary_key=True),
    Column('created_at', DateTime(timezone=True),
           server_default=func.now()),
    Column('user_id', Integer, nullable=False),
    Column('cargo_uuid', UUID, ForeignKey(
        "cargos.uuid"), nullable=False),
)


async def get_cargos(db, user_id: str):
    query = mCargo.select().where(
        mCargo.c.user_id == user_id
    )
    async with db.acquire() as conn:
        result = await conn.execute(query)
        row = await result.fetchall()
    return row


async def get_cargo(db, cargo_ref: str, user_id: str):
    query = mCargo.select().where(
        (
            mCargo.c.user_id == user_id) &
        (
            mCargo.c.uuid == cargo_ref |
            mCargo.c.name == cargo_ref
        )
    )
    async with db.acquire() as conn:
        result = await conn.execute(query)
        row = await result.fetchone()
    return row


async def delete_cargo(db, cargo_ref: str, user_id: str):
    """Remove a cargo from the database."""
    # check if cargo_uuid is a valid uuid
    # if not we consider it a name
    try:
        uuid.UUID(cargo_ref)
    except ValueError:
        query = mCargo.delete()\
            .where(
            (mCargo.c.user_id == user_id) &
            (mCargo.c.name == cargo_ref)
        )
    else:
        query = mCargo.delete()\
            .where(
            (mCargo.c.user_id == user_id) &
            (mCargo.c.uuid == cargo_ref)
        )
    async with db.acquire() as conn:
        result = await conn.execute(query.returning(mCargo.c.name))
        row = await result.fetchone()
    return row
