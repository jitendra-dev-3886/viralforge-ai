"""Repair publishing tables created before idempotency request keys existed."""
from alembic import op
from app.core.publishing_schema import ensure_publishing_request_keys

revision = "a6e013d7c243"
down_revision = "f5d902c6b132"
branch_labels = None
depends_on = None


def upgrade():
    ensure_publishing_request_keys(op.get_bind())


def downgrade():
    # f5d902c6b132 already defines this field for fresh installations.
    # Keep request keys: removing them would discard duplicate-prevention data.
    pass
