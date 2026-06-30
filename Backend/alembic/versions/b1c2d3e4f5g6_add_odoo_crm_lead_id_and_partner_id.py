"""add odoo_partner_id and odoo_crm_lead_id to leads

Revision ID: b1c2d3e4f5g6
Revises: a1b2c3d4e5f6
Create Date: 2026-06-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('leads') as batch_op:
        batch_op.add_column(sa.Column('odoo_partner_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('odoo_crm_lead_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('leads') as batch_op:
        batch_op.drop_column('odoo_crm_lead_id')
        batch_op.drop_column('odoo_partner_id')
