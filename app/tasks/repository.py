from app.tasks.models import Task
from app.extensions.db import db

class TaskRepository:

    @staticmethod
    def get_all():
        return Task.query.all()

    @staticmethod
    def get_by_id(task_id: int):
        return Task.query.get(task_id)

    @staticmethod
    def create(title: str):
        task = Task(title=title)
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def delete(task: Task):
        db.session.delete(task)
        db.session.commit()
