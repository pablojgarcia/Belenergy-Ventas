"""remove vendedor_interno discount rules

Revision ID: b4c5d6e7f8a9
Revises: a3b4c5d6e7f9
Create Date: 2026-08-19

"""
from alembic import op


revision = "b4c5d6e7f8a9"
down_revision = "a3b4c5d6e7f9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "DELETE FROM discount_rules WHERE seller_type = 'vendedor_interno'"
    )


def downgrade() -> None:
    pass