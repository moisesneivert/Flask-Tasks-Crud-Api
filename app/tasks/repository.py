"""Persistence operations for tasks."""

from __future__ import annotations

from typing import Any

from sqlalchemy import asc, desc, func, or_, select

from app.extensions import db
from app.tasks.model import Task


class TaskRepository:
    """Encapsulate task database access."""

    _SORT_FIELDS = {
        "id": Task.id,
        "title": Task.title,
        "status": Task.status,
        "priority": Task.priority,
        "due_date": Task.due_date,
        "created_at": Task.created_at,
        "updated_at": Task.updated_at,
    }

    @staticmethod
    def get(task_id: int) -> Task | None:
        return db.session.get(Task, task_id)

    @classmethod
    def list(
        cls,
        *,
        page: int,
        per_page: int,
        status: str | None,
        priority: str | None,
        search: str | None,
        sort_by: str,
        order: str,
    ) -> tuple[list[Task], int]:
        statement = select(Task)

        if status:
            statement = statement.where(Task.status == status)
        if priority:
            statement = statement.where(Task.priority == priority)
        if search:
            pattern = f"%{search.strip()}%"
            statement = statement.where(
                or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
            )

        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.session.scalar(count_statement) or 0

        sort_column = cls._SORT_FIELDS[sort_by]
        direction = desc if order == "desc" else asc
        statement = statement.order_by(direction(sort_column), asc(Task.id))
        statement = statement.offset((page - 1) * per_page).limit(per_page)

        tasks = list(db.session.scalars(statement).all())
        return tasks, total

    @staticmethod
    def create(data: dict[str, Any]) -> Task:
        task = Task(**data)
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def update(task: Task, data: dict[str, Any]) -> Task:
        for field, value in data.items():
            setattr(task, field, value)
        db.session.commit()
        return task

    @staticmethod
    def delete(task: Task) -> None:
        db.session.delete(task)
        db.session.commit()
