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


def upgrade():
    op.create_table(
        'config',
        sa.Column('id', sa.String(), primary_key=True, nullable=False),
        sa.Column('key', sa.String(), nullable=False, index=True),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('environment_id', sa.String(), nullable=True),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('key', 'version', 'environment_id', 'user_id', name='uix_key_version_env_user'),
    )

def downgrade():
    op.drop_table('config')
