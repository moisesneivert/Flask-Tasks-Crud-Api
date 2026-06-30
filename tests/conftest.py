"""Shared pytest fixtures."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.extensions import db


@pytest.fixture
def app(tmp_path: Path) -> Iterator[Flask]:
    database_path = tmp_path / "test.db"
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
        }
    )

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def task_payload() -> dict[str, object]:
    return {
        "title": "Write integration tests",
        "description": "Cover every task endpoint.",
        "status": "in_progress",
        "priority": "high",
        "due_date": "2026-07-15",
    }
