"""Initial migration

Revision ID: 5d69f3be41f3
Revises: c30f9ee2f89a
Create Date: 2024-12-10 13:01:57.022343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d69f3be41f3'
down_revision: Union[str, None] = 'c30f9ee2f89a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
