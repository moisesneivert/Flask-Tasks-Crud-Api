from flask import Blueprint, request, jsonify
from app.tasks.repository import TaskRepository
from app.tasks.schemas import TaskCreateSchema

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"])
def list_tasks():
    tasks = TaskRepository.get_all()
    return jsonify([
        {"id": t.id, "title": t.title, "completed": t.completed}
        for t in tasks
    ])

@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json()
    schema = TaskCreateSchema.from_dict(data)

    task = TaskRepository.create(schema.title)
    return jsonify({"id": task.id, "title": task.title}), 201

@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = TaskRepository.get_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    TaskRepository.delete(task)
    return "", 204
