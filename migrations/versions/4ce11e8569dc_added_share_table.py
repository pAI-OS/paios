"""added share table

Revision ID: 4ce11e8569dc
Revises: f5235ab5e888
Create Date: 2024-08-22 15:52:22.967260

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4ce11e8569dc'
down_revision: Union[str, None] = 'f5235ab5e888'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('share',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('resource_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('expiration_dt', sa.DateTime(), nullable=True),
    sa.Column('is_revoked', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('share')
