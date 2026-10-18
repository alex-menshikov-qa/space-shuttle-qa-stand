"""limit user field lengths

Matches the max lengths in app/validation.py (name 50, email 254). The values
are written out on purpose: a migration must not change when the code does.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-18
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("users", "name", type_=sa.String(50), existing_type=sa.Text())
    op.alter_column("users", "email", type_=sa.String(254), existing_type=sa.Text())


def downgrade() -> None:
    op.alter_column("users", "email", type_=sa.Text(), existing_type=sa.String(254))
    op.alter_column("users", "name", type_=sa.Text(), existing_type=sa.String(50))
