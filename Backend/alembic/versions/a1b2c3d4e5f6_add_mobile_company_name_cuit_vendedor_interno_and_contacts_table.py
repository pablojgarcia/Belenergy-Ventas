"""add mobile, company_name, cuit, vendedor_interno to customers + contacts table

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

    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('odoo_id', sa.Integer(), nullable=True),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)
    op.create_index(op.f('ix_contacts_odoo_id'), 'contacts', ['odoo_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_contacts_odoo_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_table('contacts')
    op.drop_column('customers', 'vendedor_interno')
    op.drop_column('customers', 'cuit')
    op.drop_column('customers', 'company_name')
    op.drop_column('customers', 'mobile')
