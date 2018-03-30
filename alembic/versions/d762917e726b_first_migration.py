"""First migration

Revision ID: d762917e726b
Revises:
Create Date: 2018-03-26 21:15:25.572358

"""
from alembic import op
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID


# revision identifiers, used by Alembic.
revision = 'd762917e726b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Blueprints table #
    op.create_table(
        'blueprints',
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

    # APIs table #
    op.create_table(
        'apis',
        Column('uuid', UUID, primary_key=True),
        Column('name', String(100), unique=True),
        Column('created_at', DateTime(timezone=True),
               server_default=func.now()),
        Column('specs', JSONB),
        Column('description', String(255)),
        Column('status', Integer, default=0),

        Column('user_id', Integer, nullable=False),
        Column('blueprint_uuid', UUID, ForeignKey("blueprints.uuid"),
               nullable=False),
    )

    # Cargos table #
    op.create_table(
        'cargos',
        Column('uuid', UUID, primary_key=True),
        Column('name', String(100), unique=True),
        Column('specs', JSONB),
        Column('status', Integer, default=0),
        Column('created_at', DateTime(timezone=True),
               server_default=func.now()),

        Column('user_id', Integer, nullable=False),
    )

    op.create_table(
        'user_cargos',
        Column('id', Integer, primary_key=True),
        Column('created_at', DateTime(timezone=True),
               server_default=func.now()),
        Column('user_id', Integer, nullable=False),
        Column('cargo_uuid', UUID, ForeignKey(
            "cargos.uuid"), nullable=False),
    )

    # Jobs table #
    op.create_table(
        'jobs',
        Column('uuid', UUID, primary_key=True),
        Column('name', String(100), unique=True),
        Column('created_at', DateTime(timezone=True),
               server_default=func.now()),
        Column('specs', JSONB),
        Column('description', String(255)),
        Column('status', Integer, default=0),
        Column('user_id', Integer, nullable=False),
        Column('blueprint_uuid', UUID,
               ForeignKey("blueprints.uuid"), nullable=False),
    )

    # Probes table #
    op.create_table(
        'probes',
        Column('uuid', UUID, primary_key=True),
        Column('name', String(100), unique=True),
        Column('created_at', DateTime(timezone=True),
               server_default=func.now()),
        Column('description', String(255)),
        Column('specs', JSONB),
        Column('token', String(45)),
        Column('status', Integer, default=0),

        Column('user_id', Integer, nullable=False),
        Column('blueprint_uuid', UUID, ForeignKey("blueprints.uuid"),
               nullable=False),
    )

    op.create_table(
        'user_probes',
        Column('id', Integer, primary_key=True),
        Column('created_at', DateTime(timezone=True),
               server_default=func.now()),
        Column('probe_uuid', UUID, ForeignKey("probes.uuid"), nullable=False),
        Column('user_id', Integer, nullable=False),
    )


def downgrade():
    pass
