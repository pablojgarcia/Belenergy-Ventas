"""drop leads table and add new_client columns to quotation_drafts

Revision ID: e1f2a3b4c5d6
Revises: d1e2f3a4b5c6
Create Date: 2026-07-31

"""
from alembic import op
import sqlalchemy as sa


revision = "e1f2a3b4c5d6"
down_revision = "d1e2f3a4b5c6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("DROP TABLE IF EXISTS leads CASCADE")
    op.execute("ALTER TABLE quotation_drafts ADD COLUMN IF NOT EXISTS new_client_name VARCHAR")
    op.execute("ALTER TABLE quotation_drafts ADD COLUMN IF NOT EXISTS new_client_vat VARCHAR")


def downgrade() -> None:
    op.execute("ALTER TABLE quotation_drafts DROP COLUMN IF EXISTS new_client_vat")
    op.execute("ALTER TABLE quotation_drafts DROP COLUMN IF EXISTS new_client_name")
