"""remove account name uniqueness

Revision ID: 8895ebcf7edc
Revises: 878c9c52880c
Create Date: 2026-08-28 16:39:56.051489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8895ebcf7edc'
down_revision: Union[str, Sequence[str], None] = '878c9c52880c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_user_account_name",
        "accounts",
        type_="unique",
    )


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_user_account_name",
        "accounts",
        ["user_id", "name"],
    )
