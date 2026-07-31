"""add unique constraint on contacts odoo_id

Revision ID: d1e2f3a4b5c6
Revises: b1c2d3e4f5g6
Create Date: 2026-07-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


revision = "d1e2f3a4b5c6"
down_revision = "b1c2d3e4f5g6"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    exists = bind.exec_driver_sql(
        "SELECT 1 FROM information_schema.table_constraints "
        "WHERE constraint_name = 'uq_contacts_odoo_id' AND table_schema = 'public' AND table_name = 'contacts'"
    ).scalar()
    if not exists:
        op.create_unique_constraint("uq_contacts_odoo_id", "contacts", ["odoo_id"])


def downgrade():
    op.drop_constraint("uq_contacts_odoo_id", "contacts", type_="unique")
