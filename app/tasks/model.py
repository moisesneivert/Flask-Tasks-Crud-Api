"""Task database model."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import CheckConstraint, Date, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.extensions import db
from app.tasks.enums import TaskPriority, TaskStatus


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def to_iso(value: date | datetime | None) -> str | None:
    """Serialize dates and datetimes using ISO 8601."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        return value.isoformat().replace("+00:00", "Z")
    return value.isoformat()


class Task(db.Model):
    """A task managed by the API."""

    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed')",
            name="ck_tasks_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tasks_priority",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TaskStatus.PENDING.value,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default=TaskPriority.MEDIUM.value,
        index=True,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the task."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "due_date": to_iso(self.due_date),
            "completed_at": to_iso(self.completed_at),
            "created_at": to_iso(self.created_at),
            "updated_at": to_iso(self.updated_at),
        }
