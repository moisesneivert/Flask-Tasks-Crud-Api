"""Validation helpers for task requests."""

from __future__ import annotations

from datetime import date
from typing import Any

from flask import Request

from app.errors import UnsupportedMediaTypeError, ValidationError
from app.tasks.enums import TaskPriority, TaskStatus

ALLOWED_FIELDS = {"title", "description", "status", "priority", "due_date"}
SORTABLE_FIELDS = {"id", "title", "status", "priority", "due_date", "created_at", "updated_at"}


def get_json_object(request: Request) -> dict[str, Any]:
    """Read and validate a JSON object from the request body."""
    if not request.is_json:
        raise UnsupportedMediaTypeError()

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise ValidationError("The request body must be a JSON object.")
    return payload


def validate_task_payload(payload: dict[str, Any], *, partial: bool) -> dict[str, Any]:
    """Validate POST, PUT, or PATCH task data."""
    errors: dict[str, str] = {}
    unknown_fields = sorted(set(payload) - ALLOWED_FIELDS)

    if unknown_fields:
        errors["unknown_fields"] = f"Unsupported fields: {', '.join(unknown_fields)}."

    if partial and not payload:
        errors["body"] = "At least one field must be provided."

    if not partial and "title" not in payload:
        errors["title"] = "This field is required."

    cleaned: dict[str, Any] = {}

    if "title" in payload:
        title = payload["title"]
        if not isinstance(title, str):
            errors["title"] = "Must be a string."
        else:
            title = title.strip()
            if len(title) < 3:
                errors["title"] = "Must contain at least 3 characters."
            elif len(title) > 120:
                errors["title"] = "Must contain at most 120 characters."
            else:
                cleaned["title"] = title

    if "description" in payload:
        description = payload["description"]
        if description is not None and not isinstance(description, str):
            errors["description"] = "Must be a string or null."
        elif isinstance(description, str) and len(description.strip()) > 1000:
            errors["description"] = "Must contain at most 1000 characters."
        else:
            cleaned["description"] = description.strip() if isinstance(description, str) else None

    if "status" in payload:
        status = payload["status"]
        valid_statuses = [item.value for item in TaskStatus]
        if status not in valid_statuses:
            errors["status"] = f"Must be one of: {', '.join(valid_statuses)}."
        else:
            cleaned["status"] = status

    if "priority" in payload:
        priority = payload["priority"]
        valid_priorities = [item.value for item in TaskPriority]
        if priority not in valid_priorities:
            errors["priority"] = f"Must be one of: {', '.join(valid_priorities)}."
        else:
            cleaned["priority"] = priority

    if "due_date" in payload:
        due_date = payload["due_date"]
        if due_date is None:
            cleaned["due_date"] = None
        elif not isinstance(due_date, str):
            errors["due_date"] = "Must use the YYYY-MM-DD format or null."
        else:
            try:
                cleaned["due_date"] = date.fromisoformat(due_date)
            except ValueError:
                errors["due_date"] = "Must be a valid date in YYYY-MM-DD format."

    if errors:
        raise ValidationError(details=errors)

    if not partial:
        cleaned.setdefault("description", None)
        cleaned.setdefault("status", TaskStatus.PENDING.value)
        cleaned.setdefault("priority", TaskPriority.MEDIUM.value)
        cleaned.setdefault("due_date", None)

    return cleaned


def parse_positive_int(value: str | None, *, field: str, default: int, maximum: int) -> int:
    """Parse a bounded positive integer query parameter."""
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError as error:
        raise ValidationError(details={field: "Must be an integer."}) from error
    if parsed < 1 or parsed > maximum:
        raise ValidationError(details={field: f"Must be between 1 and {maximum}."})
    return parsed
