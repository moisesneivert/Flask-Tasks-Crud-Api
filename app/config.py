"""Application configuration."""

import os
from pathlib import Path
from typing import Any


class Config:
    """Default application configuration."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024


def build_database_uri(instance_path: str) -> str:
    """Return the configured database URI or a local SQLite URI."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Some hosting providers still expose the deprecated postgres:// prefix.
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        return database_url

    database_path = Path(instance_path) / "tasks.db"
    return f"sqlite:///{database_path.as_posix()}"


def apply_runtime_config(app: Any) -> None:
    """Apply configuration values that depend on the Flask instance path."""
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", build_database_uri(app.instance_path))
