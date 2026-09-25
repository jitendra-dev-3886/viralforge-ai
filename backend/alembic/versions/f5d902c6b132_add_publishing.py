"""Add connected publishing accounts and durable posting records."""
from alembic import op
from app.models.publishing import PublishingAccount, PublishingOAuthState, PublishJob, PublishEvent

revision = "f5d902c6b132"
down_revision = "e4c891b5a021"
branch_labels = None
depends_on = None


def upgrade():
    for model in (PublishingAccount, PublishingOAuthState, PublishJob, PublishEvent):
        model.__table__.create(op.get_bind(), checkfirst=True)


def downgrade():
    for model in (PublishEvent, PublishJob, PublishingOAuthState, PublishingAccount):
        model.__table__.drop(op.get_bind(), checkfirst=True)
