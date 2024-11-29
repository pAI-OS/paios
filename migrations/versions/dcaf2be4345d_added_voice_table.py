"""added voice table

Revision ID: dcaf2be4345d
Revises: d34acf83524e
Create Date: 2024-09-04 15:13:16.956800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'dcaf2be4345d'
down_revision: Union[str, None] = 'd34acf83524e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
# Check if the persona table already exists
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'voice'):
        # Create the voice table if it doesn't exist
        op.create_table(
            'voice',
            sa.Column('id',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('xi_id',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('image_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.Column('sample_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

def downgrade() -> None:
    # Drop the voice table if it exists
    conn = op.get_bind()
    if conn.dialect.has_table(conn, 'voice'):
        op.drop_table('voice')