"""rename user password field

Revision ID: 9da0370b7725
Revises: 4c61018afaf2
Create Date: 2024-03-31 21:26:13.367127

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9da0370b7725'
down_revision: Union[str, None] = '4c61018afaf2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'password', new_column_name='hashed_password')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'hashed_password', new_column_name='password')
    # ### end Alembic commands ###
