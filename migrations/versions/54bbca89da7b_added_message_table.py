"""added message table

Revision ID: 54bbca89da7b
Revises: 29df33c77244
Create Date: 2024-07-29 13:15:31.144676

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '54bbca89da7b'
down_revision: Union[str, None] = '29df33c77244'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if the message table already exists
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'message'):
        # Create the message table if it doesn't exist
        op.create_table(
            'message',
            sa.Column('id',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('assistant_id',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('conversation_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('timestamp',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('prompt',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.Column('chat_response',  sqlmodel.sql.sqltypes.AutoString(), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    # Drop the message table if it exists
    conn = op.get_bind()
    if conn.dialect.has_table(conn, 'message'):
        op.drop_table('message')
