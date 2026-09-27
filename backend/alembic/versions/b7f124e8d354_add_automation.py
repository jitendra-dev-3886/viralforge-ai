"""Add recurring content generation rules and occurrence history."""
from alembic import op
from app.models.automation import AutomationRule, AutomationRun

revision = "b7f124e8d354"
down_revision = "a6e013d7c243"
branch_labels = None
depends_on = None


def upgrade():
    for model in (AutomationRule, AutomationRun):
        model.__table__.create(op.get_bind(), checkfirst=True)


def downgrade():
    for model in (AutomationRun, AutomationRule):
        model.__table__.drop(op.get_bind(), checkfirst=True)
