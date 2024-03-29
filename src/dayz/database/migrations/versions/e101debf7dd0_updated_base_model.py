"""updated base model

Revision ID: e101debf7dd0
Revises: ceaba82c9d26
Create Date: 2024-01-12 19:10:49.129947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e101debf7dd0'
down_revision: Union[str, None] = 'ceaba82c9d26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('servers', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('servers', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('servers', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_servers_id'), 'servers', ['id'], unique=False)
    op.add_column('users', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), nullable=False))
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_column('users', 'is_deleted')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'created_at')
    op.drop_index(op.f('ix_servers_id'), table_name='servers')
    op.drop_column('servers', 'is_deleted')
    op.drop_column('servers', 'updated_at')
    op.drop_column('servers', 'created_at')
    # ### end Alembic commands ###
