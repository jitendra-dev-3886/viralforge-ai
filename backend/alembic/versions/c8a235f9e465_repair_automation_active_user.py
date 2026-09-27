"""Repair existing Auto Mode tables missing the per-user generation lock."""
from alembic import op
from app.core.automation_schema import ensure_automation_active_user

revision = "c8a235f9e465"
down_revision = "b7f124e8d354"
branch_labels = None
depends_on = None


def upgrade():
    ensure_automation_active_user(op.get_bind())


def downgrade():
    # Fresh b7f124e8d354 tables already include this column and constraint.
    pass
