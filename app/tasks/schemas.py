from dataclasses import dataclass

@dataclass(frozen=True)
class TaskCreateSchema:
    title: str

    @staticmethod
    def from_dict(data: dict):
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("title is required")
        return TaskCreateSchema(title=title.strip())
