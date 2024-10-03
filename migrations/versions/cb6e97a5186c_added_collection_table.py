"""added collection table

Revision ID: cb6e97a5186c
Revises: 0d66a93c6c1f
Create Date: 2024-05-28 11:18:05.583239

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'cb6e97a5186c'
down_revision: Union[str, None] = '0d66a93c6c1f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('collection',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('processor_config', sa.String(), nullable=True),  # Store JSON as a string in SQLite
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('collection')
