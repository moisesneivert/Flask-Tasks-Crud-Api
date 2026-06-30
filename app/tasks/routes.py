"""Task HTTP routes."""

from __future__ import annotations

from flask import Blueprint, Response, jsonify, request, url_for

from app.tasks.service import TaskService
from app.tasks.validation import get_json_object, parse_positive_int, validate_task_payload

tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/v1/tasks")


@tasks_bp.get("")
def list_tasks():
    """List tasks with optional filtering, search, sorting, and pagination."""
    page = parse_positive_int(request.args.get("page"), field="page", default=1, maximum=100000)
    per_page = parse_positive_int(
        request.args.get("per_page"),
        field="per_page",
        default=20,
        maximum=100,
    )

    tasks, meta = TaskService.list_tasks(
        page=page,
        per_page=per_page,
        status=request.args.get("status"),
        priority=request.args.get("priority"),
        search=request.args.get("q"),
        sort_by=request.args.get("sort_by", "created_at"),
        order=request.args.get("order", "desc"),
    )
    return jsonify({"data": [task.to_dict() for task in tasks], "meta": meta})


@tasks_bp.get("/<int:task_id>")
def get_task(task_id: int):
    """Return a single task."""
    task = TaskService.get_or_404(task_id)
    return jsonify({"data": task.to_dict()})


@tasks_bp.post("")
def create_task():
    """Create a task."""
    payload = get_json_object(request)
    data = validate_task_payload(payload, partial=False)
    task = TaskService.create_task(data)

    response = jsonify({"data": task.to_dict()})
    response.status_code = 201
    response.headers["Location"] = url_for("tasks.get_task", task_id=task.id, _external=True)
    return response


@tasks_bp.put("/<int:task_id>")
def replace_task(task_id: int):
    """Fully replace the editable fields of a task."""
    payload = get_json_object(request)
    data = validate_task_payload(payload, partial=False)
    task = TaskService.replace_task(task_id, data)
    return jsonify({"data": task.to_dict()})


@tasks_bp.patch("/<int:task_id>")
def update_task(task_id: int):
    """Partially update a task."""
    payload = get_json_object(request)
    data = validate_task_payload(payload, partial=True)
    task = TaskService.update_task(task_id, data)
    return jsonify({"data": task.to_dict()})


@tasks_bp.delete("/<int:task_id>")
def delete_task(task_id: int):
    """Delete a task."""
    TaskService.delete_task(task_id)
    return Response(status=204)
