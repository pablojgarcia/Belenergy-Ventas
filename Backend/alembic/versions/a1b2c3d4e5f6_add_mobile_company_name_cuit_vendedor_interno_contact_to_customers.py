"""add mobile, company_name, cuit, vendedor_interno, contact_name, contact_email to customers

Revision ID: a1b2c3d4e5f6
Revises: dfeeec4caaa8
Create Date: 2026-06-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'dfeeec4caaa8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('customers', sa.Column('mobile', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('company_name', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('cuit', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('vendedor_interno', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('contact_name', sa.String(), nullable=True))
    op.add_column('customers', sa.Column('contact_email', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('customers', 'contact_email')
    op.drop_column('customers', 'contact_name')
    op.drop_column('customers', 'vendedor_interno')
    op.drop_column('customers', 'cuit')
    op.drop_column('customers', 'company_name')
    op.drop_column('customers', 'mobile')
