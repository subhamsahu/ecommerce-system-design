"""move timestamp defaults to Python

Revision ID: 20260928_0002
Revises: 20260924_0001
Create Date: 2026-09-28
"""

from alembic import op
import sqlalchemy as sa


revision = "20260928_0002"
down_revision = "20260924_0001"
branch_labels = None
depends_on = None


TIMESTAMP_COLUMNS = (
    ("users", "created_at"),
    ("role_permissions", "updated_at"),
    ("categories", "created_at"),
    ("products", "created_at"),
    ("products", "updated_at"),
    ("inventory", "updated_at"),
    ("inventory_movements", "created_at"),
    ("carts", "created_at"),
    ("carts", "updated_at"),
    ("addresses", "created_at"),
    ("orders", "created_at"),
    ("orders", "updated_at"),
    ("order_status_history", "created_at"),
    ("payments", "created_at"),
    ("payment_status_history", "created_at"),
    ("refunds", "created_at"),
)


def upgrade() -> None:
    for table_name, column_name in TIMESTAMP_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.DateTime(timezone=True),
            server_default=None,
        )


def downgrade() -> None:
    for table_name, column_name in TIMESTAMP_COLUMNS:
        op.alter_column(
            table_name,
            column_name,
            existing_type=sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )