"""add role to user model

Revision ID: 008645bff529
Revises: 1128b8cc9a3d
Create Date: 2024-11-06 22:35:51.811621

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '008645bff529'
down_revision: Union[str, None] = '1128b8cc9a3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'role')
    # ### end Alembic commands ###
