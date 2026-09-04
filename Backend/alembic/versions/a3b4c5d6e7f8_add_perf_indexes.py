"""add perf indexes for products, discount rules, customers, drafts

Revision ID: a3b4c5d6e7f8
Revises: f2e1d4c3b2a1
Create Date: 2026-09-04

"""
from alembic import op


revision = "a3b4c5d6e7f8"
down_revision = "f2e1d4c3b2a1"
branch_labels = None
depends_on = None


INDEXES = [
    ("ix_products_product_line_id", "products", ["product_line_id"]),
    (
        "ix_discount_rules_seller_type_line",
        "discount_rules",
        ["seller_type", "product_line_id"],
    ),
    ("ix_customers_salesperson_id", "customers", ["salesperson_id"]),
    (
        "ix_quotation_drafts_customer_status",
        "quotation_drafts",
        ["customer_id", "status"],
    ),
]


def upgrade() -> None:
    for name, table, cols in INDEXES:
        op.execute(
            f"CREATE INDEX IF NOT EXISTS {name} "
            f"ON {table} ({', '.join(cols)})"
        )


def downgrade() -> None:
    for name, table, _cols in INDEXES:
        op.execute(f"DROP INDEX IF EXISTS {name}")
