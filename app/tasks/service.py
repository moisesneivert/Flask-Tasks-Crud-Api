"""Task application service."""

from __future__ import annotations

from datetime import UTC, datetime
from math import ceil
from typing import Any

from app.errors import NotFoundError, ValidationError
from app.tasks.enums import TaskPriority, TaskStatus
from app.tasks.model import Task
from app.tasks.repository import TaskRepository
from app.tasks.validation import SORTABLE_FIELDS


class TaskService:
    """Coordinate validation-independent task business rules."""

    @staticmethod
    def get_or_404(task_id: int) -> Task:
        task = TaskRepository.get(task_id)
        if task is None:
            raise NotFoundError(f"Task {task_id} was not found.")
        return task

    @staticmethod
    def list_tasks(
        *,
        page: int,
        per_page: int,
        status: str | None,
        priority: str | None,
        search: str | None,
        sort_by: str,
        order: str,
    ) -> tuple[list[Task], dict[str, Any]]:
        valid_statuses = [item.value for item in TaskStatus]
        valid_priorities = [item.value for item in TaskPriority]
        errors: dict[str, str] = {}

        if status and status not in valid_statuses:
            errors["status"] = f"Must be one of: {', '.join(valid_statuses)}."
        if priority and priority not in valid_priorities:
            errors["priority"] = f"Must be one of: {', '.join(valid_priorities)}."
        if sort_by not in SORTABLE_FIELDS:
            errors["sort_by"] = f"Must be one of: {', '.join(sorted(SORTABLE_FIELDS))}."
        if order not in {"asc", "desc"}:
            errors["order"] = "Must be either asc or desc."
        if search is not None and len(search.strip()) > 100:
            errors["q"] = "Must contain at most 100 characters."

        if errors:
            raise ValidationError(details=errors)

        tasks, total = TaskRepository.list(
            page=page,
            per_page=per_page,
            status=status,
            priority=priority,
            search=search,
            sort_by=sort_by,
            order=order,
        )
        pages = ceil(total / per_page) if total else 0
        meta = {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "has_next": page < pages,
            "has_previous": page > 1 and pages > 0,
        }
        return tasks, meta

    @staticmethod
    def create_task(data: dict[str, Any]) -> Task:
        data = TaskService._apply_completion_timestamp(data)
        return TaskRepository.create(data)

    @staticmethod
    def replace_task(task_id: int, data: dict[str, Any]) -> Task:
        task = TaskService.get_or_404(task_id)
        data = TaskService._apply_completion_timestamp(data, current_status=task.status)
        return TaskRepository.update(task, data)

    @staticmethod
    def update_task(task_id: int, data: dict[str, Any]) -> Task:
        task = TaskService.get_or_404(task_id)
        data = TaskService._apply_completion_timestamp(data, current_status=task.status)
        return TaskRepository.update(task, data)

    @staticmethod
    def delete_task(task_id: int) -> None:
        task = TaskService.get_or_404(task_id)
        TaskRepository.delete(task)

    @staticmethod
    def _apply_completion_timestamp(
        data: dict[str, Any],
        *,
        current_status: str | None = None,
    ) -> dict[str, Any]:
        updated = data.copy()
        new_status = updated.get("status", current_status)

        if new_status == TaskStatus.COMPLETED.value and current_status != new_status:
            updated["completed_at"] = datetime.now(UTC)
        elif new_status != TaskStatus.COMPLETED.value and (
            current_status == TaskStatus.COMPLETED.value or current_status is None
        ):
            updated["completed_at"] = None

        return updated
