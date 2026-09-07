"""add new_client_is_company to quotation_drafts

Revision ID: a5b6c7d8e9f0
Revises: b4c5d6e7f8a9
Create Date: 2026-09-07

"""
from alembic import op


revision = "a5b6c7d8e9f0"
down_revision = "b4c5d6e7f8a9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE quotation_drafts ADD COLUMN IF NOT EXISTS new_client_is_company BOOLEAN")


def downgrade() -> None:
    op.execute("ALTER TABLE quotation_drafts DROP COLUMN IF EXISTS new_client_is_company")