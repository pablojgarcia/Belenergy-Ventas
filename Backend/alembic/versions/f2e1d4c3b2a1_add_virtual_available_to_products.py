"""add virtual_available to products

Revision ID: f2e1d4c3b2a1
Revises: e1f2a3b4c5d6
Create Date: 2026-08-17

"""
from alembic import op


revision = "f2e1d4c3b2a1"
down_revision = "e1f2a3b4c5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE products ADD COLUMN IF NOT EXISTS virtual_available FLOAT DEFAULT 0.0")


def downgrade() -> None:
    op.execute("ALTER TABLE products DROP COLUMN IF EXISTS virtual_available")
