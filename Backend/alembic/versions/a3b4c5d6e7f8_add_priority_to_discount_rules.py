"""add priority to discount_rules

Revision ID: a3b4c5d6e7f8
Revises: f2e1d4c3b2a1
Create Date: 2026-08-19

"""
from alembic import op


revision = "a3b4c5d6e7f8"
down_revision = "f2e1d4c3b2a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE discount_rules ADD COLUMN IF NOT EXISTS priority INTEGER NOT NULL DEFAULT 0"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE discount_rules DROP COLUMN IF EXISTS priority")