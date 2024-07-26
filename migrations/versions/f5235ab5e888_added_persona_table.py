"""added persona table

Revision ID: f5235ab5e888
Revises: cb6e97a5186c
Create Date: 2024-07-16 15:43:22.600859

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = 'f5235ab5e888'
down_revision: Union[str, None] = 'cb6e97a5186c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if the persona table already exists
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'persona'):
        # Create the persona table if it doesn't exist
        op.create_table(
            'persona',
            sa.Column('id',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('name',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('voiceId',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('faceId',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade() -> None:
    # Drop the persona table if it exists
    conn = op.get_bind()
    if conn.dialect.has_table(conn, 'persona'):
        op.drop_table('persona')