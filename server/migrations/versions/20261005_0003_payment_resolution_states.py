"""Add explicit failed and unresolved payment order states.

Revision ID: 20261005_0003
Revises: 20260928_0002
"""

from alembic import op


revision = "20261005_0003"
down_revision = "20260928_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'payment_failed'")
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'payment_review'")


def downgrade() -> None:
    # PostgreSQL cannot drop individual enum values. Removing these states
    # also requires a policy for existing failed/unresolved orders.
    raise RuntimeError("Manual data migration is required to remove payment order states")
