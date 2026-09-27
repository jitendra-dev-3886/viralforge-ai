"""Repair Auto Mode tables created before the per-user generation lock."""
from sqlalchemy import inspect, text


def ensure_automation_active_user(connection):
    if connection.dialect.name == "postgresql":
        connection.execute(text("SELECT pg_advisory_xact_lock(174992602)"))
    inspector = inspect(connection)
    if not inspector.has_table("automation_runs"):
        return
    if "active_user" not in {column["name"] for column in inspector.get_columns("automation_runs")}:
        connection.execute(text("ALTER TABLE automation_runs ADD COLUMN active_user INTEGER"))
    inspector = inspect(connection)
    unique = inspector.get_unique_constraints("automation_runs")
    indexes = inspector.get_indexes("automation_runs")
    if not (any(item.get("column_names") == ["active_user"] for item in unique)
            or any(item.get("unique") and item.get("column_names") == ["active_user"] for item in indexes)):
        connection.execute(text("CREATE UNIQUE INDEX uq_automation_runs_active_user ON automation_runs (active_user)"))
