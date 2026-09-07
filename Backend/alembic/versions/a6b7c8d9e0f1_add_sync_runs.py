"""add sync_runs table for persisted sync status and history

Revision ID: a6b7c8d9e0f1
Revises: a5b6c7d8e9f0
Create Date: 2026-09-07

"""
from alembic import op
import sqlalchemy as sa


revision = "a6b7c8d9e0f1"
down_revision = "a5b6c7d8e9f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sync_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sync_type", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("stage", sa.String(), nullable=True),
        sa.Column("total", sa.Integer(), nullable=True),
        sa.Column("processed", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("triggered_by", sa.String(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("elapsed", sa.Float(), nullable=True),
    )
    op.create_index(op.f("ix_sync_runs_sync_type"), "sync_runs", ["sync_type"])


def downgrade() -> None:
    op.drop_index(op.f("ix_sync_runs_sync_type"), table_name="sync_runs")
    op.drop_table("sync_runs")