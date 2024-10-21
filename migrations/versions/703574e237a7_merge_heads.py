"""Merge heads

Revision ID: 703574e237a7
Revises: 187855982332, 5a1a6050b8f0
Create Date: 2024-10-21 15:51:55.515484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '703574e237a7'
down_revision: Union[str, None] = ('187855982332', '5a1a6050b8f0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
