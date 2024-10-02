"""Added cred table

Revision ID: 91d051f98616
Revises: 4ce11e8569dc
Create Date: 2024-10-02 01:31:14.538904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '91d051f98616'
down_revision: Union[str, None] = '4ce11e8569dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cred',
    sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('public_key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('webauthn_user_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('backed_up', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('transports', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['webauthn_user_id'], ['user.webauthn_user_id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('asset')

