import unittest
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import IntegrityError, ProgrammingError

from app.api.automation import router
from app.core.automation_schema import ensure_automation_active_user
from app.core.security import get_current_user_id
from app.database import get_db


class AutomationSchemaTests(unittest.TestCase):
    def test_missing_column_repaired_without_losing_history(self):
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        with engine.begin() as connection:
            connection.execute(text("CREATE TABLE automation_runs (id INTEGER PRIMARY KEY, status VARCHAR(30))"))
            connection.execute(text("INSERT INTO automation_runs VALUES (1, 'draft'), (2, 'failed')"))
            ensure_automation_active_user(connection)
            ensure_automation_active_user(connection)
            self.assertEqual(connection.execute(text("SELECT id, status, active_user FROM automation_runs ORDER BY id")).all(), [(1, "draft", None), (2, "failed", None)])
            self.assertEqual(len(inspect(connection).get_indexes("automation_runs")), 1)
            connection.execute(text("UPDATE automation_runs SET active_user = 1 WHERE id = 1"))
            with self.assertRaises(IntegrityError):
                connection.execute(text("UPDATE automation_runs SET active_user = 1 WHERE id = 2"))

    def test_fresh_constraint_is_preserved_and_missing_table_is_skipped(self):
        engine = create_engine("sqlite://")
        self.addCleanup(engine.dispose)
        with engine.begin() as connection:
            ensure_automation_active_user(connection)
            self.assertFalse(inspect(connection).has_table("automation_runs"))
            connection.execute(text("CREATE TABLE automation_runs (id INTEGER PRIMARY KEY, active_user INTEGER UNIQUE)"))
            ensure_automation_active_user(connection)
            self.assertEqual(inspect(connection).get_indexes("automation_runs"), [])

    def test_database_error_keeps_cors_and_returns_readable_message(self):
        app = FastAPI()
        app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"])
        app.include_router(router)
        db = Mock()
        db.query.side_effect = ProgrammingError("private query", {"secret": "private-token"}, Exception("missing column"))
        app.dependency_overrides[get_db] = lambda: db
        app.dependency_overrides[get_current_user_id] = lambda: 1
        with TestClient(app, raise_server_exceptions=False) as client, self.assertLogs("app.core.scheduling_route", level="ERROR"):
            response = client.get("/api/automations/", headers={"Origin": "http://localhost:5173"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.headers["access-control-allow-origin"], "http://localhost:5173")
        self.assertIn("scheduling database", response.json()["detail"])
        self.assertNotIn("private-token", response.text)


if __name__ == "__main__":
    unittest.main()
