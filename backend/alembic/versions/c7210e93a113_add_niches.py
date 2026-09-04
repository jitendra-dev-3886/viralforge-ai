"""add niches

Revision ID: c7210e93a113
Revises: 8f27b94a1e20
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "c7210e93a113"
down_revision: Union[str, None] = "8f27b94a1e20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if "niches" in sa.inspect(op.get_bind()).get_table_names():
        return
    op.create_table(
        "niches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(20), nullable=True),
        sa.Column("color", sa.String(30), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "name", name="uq_niches_user_name"),
    )
    op.create_index("ix_niches_id", "niches", ["id"])
    op.create_index("ix_niches_user_id", "niches", ["user_id"])


def downgrade() -> None:
    if "niches" not in sa.inspect(op.get_bind()).get_table_names():
        return
    op.drop_index("ix_niches_user_id", table_name="niches")
    op.drop_index("ix_niches_id", table_name="niches")
    op.drop_table("niches")
