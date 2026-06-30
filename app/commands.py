"""Custom Flask CLI commands."""

from datetime import date, timedelta

import click
from flask import Flask

from app.extensions import db
from app.tasks.enums import TaskPriority, TaskStatus
from app.tasks.model import Task


def register_commands(app: Flask) -> None:
    """Register development utility commands."""

    @app.cli.command("seed")
    def seed_database() -> None:
        """Insert sample tasks when the database is empty."""
        if db.session.query(Task.id).first() is not None:
            click.echo("Seed skipped: the tasks table already contains data.")
            return

        today = date.today()
        db.session.add_all(
            [
                Task(
                    title="Review API documentation",
                    description="Check endpoint examples and response formats.",
                    priority=TaskPriority.HIGH.value,
                    due_date=today + timedelta(days=2),
                ),
                Task(
                    title="Configure continuous integration",
                    description="Run lint and tests on every pull request.",
                    status=TaskStatus.IN_PROGRESS.value,
                    priority=TaskPriority.MEDIUM.value,
                    due_date=today + timedelta(days=5),
                ),
            ]
        )
        db.session.commit()
        click.echo("Sample tasks created.")
