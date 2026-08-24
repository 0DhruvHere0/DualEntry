"""add transaction counterparty

Revision ID: 63c680a557f8
Revises: daa3b9c53ae2
Create Date: 2026-08-24 19:17:15.645561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63c680a557f8'
down_revision: Union[str, Sequence[str], None] = 'daa3b9c53ae2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Add the column temporarily as nullable
    op.add_column(
        "transactions",
        sa.Column(
            "counterpart_id",
            sa.Integer(),
            nullable=True
        )
    )

    # 2. Existing transactions were loans from Rahul (User 2)
    op.execute(
        """
        UPDATE transactions
        SET counterpart_id = 2
        WHERE counterpart_id IS NULL
        """
    )

    # 3. Make the column required for all future transactions
    op.alter_column(
        "transactions",
        "counterpart_id",
        existing_type=sa.Integer(),
        nullable=False
    )

    # 4. Connect counterparty_id to users.id
    op.create_foreign_key(
        "fk_transactions_counterpart_id_users",
        "transactions",
        "users",
        ["counterpart_id"],
        ["id"]
    )    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_transactions_counterpart_id_users",
        "transactions",
        type_="foreignkey"
    )

    op.drop_column(
        "transactions",
        "counterpart_id"
    )    # ### end Alembic commands ###
