"""added asset table

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
    op.create_table('asset',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('creator', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('subject', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('asset')
