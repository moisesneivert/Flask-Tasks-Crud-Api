"""Flask application factory."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify

from app.commands import register_commands
from app.config import Config, apply_runtime_config
from app.errors import register_error_handlers
from app.extensions import db, migrate
from app.health.routes import health_bp
from app.tasks.routes import tasks_bp


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    """Create and configure the Flask application."""
    load_dotenv()

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    if test_config:
        app.config.update(test_config)
    apply_runtime_config(app)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(health_bp)
    app.register_blueprint(tasks_bp)
    register_error_handlers(app)
    register_commands(app)

    @app.get("/")
    def index():
        return jsonify(
            {
                "name": "Flask Tasks CRUD API",
                "version": "1.0.0",
                "health": "/health",
                "tasks": "/api/v1/tasks",
            }
        )

    return app
