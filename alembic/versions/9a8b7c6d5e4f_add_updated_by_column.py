"""Add updated_by column to all tables

Revision ID: 9a8b7c6d5e4f
Revises: 09bd630eae6e
Create Date: 2026-06-11 03:37:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a8b7c6d5e4f'
down_revision: Union[str, None] = '09bd630eae6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TABLES = [
    'death_reasons',
    'external_sources',
    'internal_sources',
    'procedure_delay_categories',
    'procedure_delay_causes',
    'procedures',
    'regions',
    'theatre_member_roles',
    'theatre_members',
    'theatre_record_delays',
    'theatre_record_team_members',
    'theatre_roles',
    'theatre_time_records',
    'theatre_units',
]


def upgrade() -> None:
    for table_name in TABLES:
        op.add_column(
            table_name,
            sa.Column('updated_by', sa.Integer(), nullable=True)
        )


def downgrade() -> None:
    for table_name in TABLES:
        op.drop_column(table_name, 'updated_by')