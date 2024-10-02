"""Added user table

Revision ID: 0d66a93c6c1f
Revises: 75aaaf2cd1a2
Create Date: 2024-05-08 10:49:22.471591

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '0d66a93c6c1f'
down_revision: Union[str, None] = '75aaaf2cd1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('webauthn_user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False, unique=True),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False, unique=True),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('user')
