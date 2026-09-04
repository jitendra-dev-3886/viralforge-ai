"""add social accounts

Revision ID: 8f27b94a1e20
Revises: 3e1aa46a5d2d
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "8f27b94a1e20"
down_revision: Union[str, Sequence[str], None] = "3e1aa46a5d2d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    password_column = next(column for column in inspector.get_columns("users") if column["name"] == "hashed_password")
    if not password_column["nullable"]:
        op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=True)

    if not inspector.has_table("social_accounts"):
        op.create_table(
            "social_accounts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("provider", sa.String(30), nullable=False),
            sa.Column("provider_user_id", sa.String(255), nullable=False),
            sa.Column("username", sa.String(255), nullable=True),
            sa.Column("avatar_url", sa.String(1000), nullable=True),
            sa.Column("profile_data", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("last_login_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.UniqueConstraint("provider", "provider_user_id", name="uq_social_provider_user"),
        )
        op.create_index("ix_social_accounts_user_id", "social_accounts", ["user_id"])
        op.create_index("ix_social_accounts_provider", "social_accounts", ["provider"])


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("social_accounts"):
        op.drop_table("social_accounts")
    password_column = next(column for column in sa.inspect(op.get_bind()).get_columns("users") if column["name"] == "hashed_password")
    if password_column["nullable"]:
        op.alter_column("users", "hashed_password", existing_type=sa.String(255), nullable=False)
