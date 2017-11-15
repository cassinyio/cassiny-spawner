"""
Cargos models.

:copyright: (c) 2017, Cassiny.io OÜ.
All rights reserved.
"""

from sqlalchemy import (
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

mSpaceDock = Table('spacedocks', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('name', String(255)),
                   Column('url', String(255)),
                   Column('size', Integer, default=10),
                   Column('created_at', DateTime(timezone=True),
                          server_default=func.now()),
                   Column('description', Unicode(255)),
                   )

mCargo = Table('cargos', metadata,
               Column('id', Integer, primary_key=True),
               # name and subdomain of the service
               Column('name', String(100), unique=True),

               Column('access_key', String(25)),
               Column('secret_key', String(45)),

               Column('description', Unicode(255)),

               # if the service is running or not
               Column('active', Boolean, default=False),

               Column('size', Integer, default=10),
               Column('created_at', DateTime(timezone=True),
                      server_default=func.now()),
               # server where the cargo is hosted
               Column('user_id', Integer, nullable=False),
               # server where the cargo is hosted
               Column('spacedock_id', Integer,
                      ForeignKey("spacedocks.id"), nullable=False),
               )

mUser_cargos = Table('user_cargos', metadata,
                     Column('id', Integer, primary_key=True),
                     # ID of the container
                     Column('created_at', DateTime(timezone=True),
                            server_default=func.now()),

                     # Creator of the Container
                     Column('user_id', Integer, nullable=False),
                     Column('cargo_id', Integer, ForeignKey(
                         "cargos.id"), nullable=False),
                     )
