"""add schedule content

Revision ID: e4c891b5a021
Revises: d3b781a4f920
"""
from alembic import op
import sqlalchemy as sa
revision="e4c891b5a021"; down_revision="d3b781a4f920"; branch_labels=None; depends_on=None
def upgrade():
    columns={c["name"] for c in sa.inspect(op.get_bind()).get_columns("schedules")}
    if "content_id" not in columns:
        op.add_column("schedules",sa.Column("content_id",sa.Integer(),nullable=True))
        op.create_foreign_key("fk_schedules_content_id","schedules","contents",["content_id"],["id"],ondelete="CASCADE")
        op.create_index("ix_schedules_content_id","schedules",["content_id"])
def downgrade():
    columns={c["name"] for c in sa.inspect(op.get_bind()).get_columns("schedules")}
    if "content_id" in columns:
        op.drop_index("ix_schedules_content_id",table_name="schedules"); op.drop_constraint("fk_schedules_content_id","schedules",type_="foreignkey"); op.drop_column("schedules","content_id")
