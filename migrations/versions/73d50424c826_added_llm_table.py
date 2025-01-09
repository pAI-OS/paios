"""added llm table

Revision ID: 73d50424c826
Revises: 187855982332
Create Date: 2024-10-10 17:31:43.949960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '73d50424c826'
down_revision: Union[str, None] = '187855982332'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('llm',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('aisuite_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('llm_name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('api_base', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('llm')
