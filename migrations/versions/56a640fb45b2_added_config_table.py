"""Config model

Revision ID: 56a640fb45b2
Revises: 
Create Date: 2024-05-06 22:36:16.566789

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '56a640fb45b2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('config',
    sa.Column('key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('value', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('key')
    )


def downgrade() -> None:
    op.drop_table('config')
