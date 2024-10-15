"""share convert user to FK

Revision ID: 4716615fdc5d
Revises: 187855982332
Create Date: 2024-10-03 12:24:37.618156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '4716615fdc5d'
down_revision: Union[str, None] = '187855982332'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('share', schema=None) as batch_op:
        batch_op.create_foreign_key('user_id', 'user', ['user_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('share', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
