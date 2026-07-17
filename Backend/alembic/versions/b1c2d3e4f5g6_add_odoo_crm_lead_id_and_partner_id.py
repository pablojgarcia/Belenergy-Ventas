"""add odoo_partner_id and odoo_crm_lead_id to leads (no-op, columns in c1b2c3d4e5f6)

Revision ID: b1c2d3e4f5g6
Revises: c1b2c3d4e5f6
Create Date: 2026-06-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = 'c1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
