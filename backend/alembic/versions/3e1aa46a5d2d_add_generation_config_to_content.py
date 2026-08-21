"""add generation config to content

Revision ID: 3e1aa46a5d2d
Revises:
Create Date: 2026-08-17 23:20:27.822011
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3e1aa46a5d2d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add generation_config to contents table."""

    op.add_column(
        "contents",
        sa.Column(
            "generation_config",
            sa.JSON(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Remove generation_config from contents table."""

    op.drop_column(
        "contents",
        "generation_config"
    )