"""rename counterparty to counterpart

Revision ID: 7c259bc32670
Revises: 63c680a557f8
Create Date: 2026-08-24 19:34:50.541313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c259bc32670'
down_revision: Union[str, Sequence[str], None] = '63c680a557f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "transactions",
        "counterparty_id",
        new_column_name="counterpart_id"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "transactions",
        "counterpart_id",
        new_column_name="counterparty_id"
    )
    # ### end Alembic commands ###
