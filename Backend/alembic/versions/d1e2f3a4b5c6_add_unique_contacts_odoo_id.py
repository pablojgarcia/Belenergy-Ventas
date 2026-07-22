"""add unique constraint on contacts odoo_id

Revision ID: d1e2f3a4b5c6
Revises: c1b2c3d4e5f6
Create Date: 2026-07-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "d1e2f3a4b5c6"
down_revision = "c1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_unique_constraint("uq_contacts_odoo_id", "contacts", ["odoo_id"])


def downgrade():
    op.drop_constraint("uq_contacts_odoo_id", "contacts", type_="unique")
