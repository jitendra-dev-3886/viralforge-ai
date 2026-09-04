"""add super admin

Revision ID: d3b781a4f920
Revises: c7210e93a113
"""
from alembic import op
import sqlalchemy as sa

revision = "d3b781a4f920"
down_revision = "c7210e93a113"
branch_labels = None
depends_on = None

def upgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "is_super_admin" not in columns:
        op.add_column("users", sa.Column("is_super_admin", sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    columns = {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}
    if "is_super_admin" in columns:
        op.drop_column("users", "is_super_admin")
