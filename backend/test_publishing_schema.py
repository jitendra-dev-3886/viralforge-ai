import unittest
from unittest.mock import Mock
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from sqlalchemy import Column, Integer, MetaData, String, Table, create_engine, inspect, text
from sqlalchemy.exc import IntegrityError, ProgrammingError

from app.api.schedule import router
from app.core.publishing_schema import ensure_publishing_request_keys
from app.core.security import get_current_user_id
from app.database import get_db


class PublishingSchemaTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        self.addCleanup(self.engine.dispose)

    def test_legacy_jobs_are_preserved_and_receive_unique_request_keys(self):
        with self.engine.begin() as connection:
            connection.execute(text("CREATE TABLE publish_jobs (id INTEGER PRIMARY KEY, status VARCHAR(30), payload TEXT)"))
            connection.execute(text("INSERT INTO publish_jobs (id, status, payload) VALUES (1, 'queued', 'first'), (2, 'published', 'second')"))
            ensure_publishing_request_keys(connection)
            rows = connection.execute(text("SELECT id, status, payload, request_key FROM publish_jobs ORDER BY id")).all()
            self.assertEqual([tuple(row[:3]) for row in rows], [(1, "queued", "first"), (2, "published", "second")])
            keys = [row.request_key for row in rows]
            self.assertEqual(len(set(keys)), 2)
            for key in keys:
                self.assertEqual(str(UUID(key)), key)
            ensure_publishing_request_keys(connection)
            self.assertEqual(connection.execute(text("SELECT request_key FROM publish_jobs ORDER BY id")).scalars().all(), keys)
        with self.engine.begin() as connection:
            with self.assertRaises(IntegrityError):
                connection.execute(text("INSERT INTO publish_jobs (id, request_key) VALUES (3, :key)"), {"key": keys[0]})

    def test_existing_unique_constraint_and_keys_are_preserved(self):
        with self.engine.begin() as connection:
            Table(
                "publish_jobs", MetaData(),
                Column("id", Integer, primary_key=True),
                Column("request_key", String(36), nullable=False, unique=True),
            ).create(connection)
            connection.execute(text("INSERT INTO publish_jobs (id, request_key) VALUES (1, 'already-saved')"))
            ensure_publishing_request_keys(connection)
            self.assertEqual(connection.execute(text("SELECT request_key FROM publish_jobs")).scalar_one(), "already-saved")
            self.assertFalse(inspect(connection).get_indexes("publish_jobs"))

    def test_missing_table_is_left_for_normal_table_creation(self):
        with self.engine.begin() as connection:
            ensure_publishing_request_keys(connection)
            self.assertFalse(inspect(connection).has_table("publish_jobs"))

    def test_database_failure_is_readable_by_browser_without_query_secrets(self):
        app = FastAPI()
        app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])
        app.include_router(router)
        db = Mock()
        db.query.side_effect = ProgrammingError("SELECT private query", {"secret": "private-token"}, Exception("missing column"))
        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_current_user_id] = lambda: 1
        with TestClient(app, raise_server_exceptions=False) as client, self.assertLogs("app.core.scheduling_route", level="ERROR"):
            response = client.get("/api/schedules/", headers={"Origin": "http://localhost:5173"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:5173")
        self.assertIn("scheduling database", response.json()["detail"])
        self.assertNotIn("private-token", response.text)


if __name__ == "__main__":
    unittest.main()
