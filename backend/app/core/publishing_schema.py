"""Additive repair for publishing tables created before request keys were added."""
from uuid import uuid4
from sqlalchemy import inspect, text


def ensure_publishing_request_keys(connection):
    if connection.dialect.name == "postgresql":
        # Serialize this short repair when multiple API workers start together.
        connection.execute(text("SELECT pg_advisory_xact_lock(174992601)"))
    inspector = inspect(connection)
    if not inspector.has_table("publish_jobs"):
        return
    columns = {column["name"]: column for column in inspector.get_columns("publish_jobs")}
    if "request_key" not in columns:
        connection.execute(text("ALTER TABLE publish_jobs ADD COLUMN request_key VARCHAR(36)"))
    missing = connection.execute(text("SELECT id FROM publish_jobs WHERE request_key IS NULL OR request_key = ''")).scalars().all()
    for job_id in missing:
        connection.execute(text("UPDATE publish_jobs SET request_key = :key WHERE id = :id"), {"key": str(uuid4()), "id": job_id})
    inspector = inspect(connection)
    constraints = inspector.get_unique_constraints("publish_jobs")
    indexes = inspector.get_indexes("publish_jobs")
    has_unique = any(item.get("column_names") == ["request_key"] for item in constraints)
    has_unique = has_unique or any(item.get("unique") and item.get("column_names") == ["request_key"] for item in indexes)
    if not has_unique:
        connection.execute(text("CREATE UNIQUE INDEX uq_publish_jobs_request_key ON publish_jobs (request_key)"))
    if connection.dialect.name == "postgresql" and ("request_key" not in columns or columns["request_key"]["nullable"]):
        connection.execute(text("ALTER TABLE publish_jobs ALTER COLUMN request_key SET NOT NULL"))
