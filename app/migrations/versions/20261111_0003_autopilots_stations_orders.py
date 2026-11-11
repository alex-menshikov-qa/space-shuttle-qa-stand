"""autopilots, stations, orders

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-11
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "autopilots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("login", sa.Text(), nullable=False, unique=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_table(
        "stations",
        sa.Column("number", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("color", sa.Text(), nullable=False),
    )
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("track", sa.Integer(), nullable=False, unique=True),
        sa.Column("first_name", sa.Text(), nullable=False),
        sa.Column("last_name", sa.Text(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("station_number", sa.Integer(), nullable=False),
        sa.Column("station_name", sa.Text(), nullable=False),
        sa.Column("station_color", sa.Text(), nullable=False),
        sa.Column("phone", sa.Text(), nullable=False),
        sa.Column("rent_time", sa.Integer(), nullable=False),
        sa.Column("delivery_date", sa.Date(), nullable=False),
        sa.Column("comment", sa.Text(), server_default="", nullable=False),
        sa.Column("color", sa.JSON(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("autopilot_id", sa.Integer(), nullable=True),
        sa.Column("autopilot_first_name", sa.Text(), nullable=True),
        sa.Column("autopilot_deleted", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("clock_offset_seconds", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_index("ix_orders_autopilot_id", "orders", ["autopilot_id"])


def downgrade() -> None:
    op.drop_index("ix_orders_autopilot_id", table_name="orders")
    op.drop_table("orders")
    op.drop_table("stations")
    op.drop_table("autopilots")
