"""populate default retry config values

Revision ID: 8e53bbbd6b84
Revises: 3a75613abb89
Create Date: 2026-01-05 00:34:51.766008

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '8e53bbbd6b84'
down_revision: str | Sequence[str] | None = '3a75613abb89'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE data_source_rate_limits SET max_retries = 3 WHERE max_retries IS NULL")
    op.execute("UPDATE data_source_rate_limits SET backoff_multiplier = 2 WHERE backoff_multiplier IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    pass
