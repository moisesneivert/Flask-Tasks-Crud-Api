"""Integration tests for task CRUD operations."""

from flask.testing import FlaskClient


def create_task(client: FlaskClient, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "title": "Create API documentation",
        "description": "Document every endpoint.",
        "priority": "medium",
    }
    payload.update(overrides)
    response = client.post("/api/v1/tasks", json=payload)
    assert response.status_code == 201
    return response.get_json()["data"]


def test_create_task_with_defaults(client: FlaskClient) -> None:
    response = client.post(
        "/api/v1/tasks",
        json={"title": "Configure development environment"},
    )

    body = response.get_json()
    assert response.status_code == 201
    assert response.headers["Location"].endswith("/api/v1/tasks/1")
    assert body["data"]["id"] == 1
    assert body["data"]["title"] == "Configure development environment"
    assert body["data"]["description"] is None
    assert body["data"]["status"] == "pending"
    assert body["data"]["priority"] == "medium"
    assert body["data"]["completed_at"] is None


def test_create_completed_task_sets_completion_timestamp(client: FlaskClient) -> None:
    task = create_task(client, status="completed")

    assert task["status"] == "completed"
    assert task["completed_at"] is not None
    assert str(task["completed_at"]).endswith("Z")


def test_create_task_validates_payload(client: FlaskClient) -> None:
    response = client.post(
        "/api/v1/tasks",
        json={
            "title": "  ",
            "status": "invalid",
            "priority": "urgent",
            "due_date": "15/07/2026",
            "unexpected": True,
        },
    )

    body = response.get_json()
    assert response.status_code == 400
    assert body["error"]["code"] == "validation_error"
    assert set(body["error"]["details"]) == {
        "title",
        "status",
        "priority",
        "due_date",
        "unknown_fields",
    }


def test_create_task_requires_json_content_type(client: FlaskClient) -> None:
    response = client.post("/api/v1/tasks", data="title=test")

    assert response.status_code == 415
    assert response.get_json()["error"]["code"] == "unsupported_media_type"


def test_list_tasks_supports_filters_search_and_pagination(client: FlaskClient) -> None:
    create_task(client, title="Write Python tests", priority="high", status="in_progress")
    create_task(client, title="Deploy Flask API", priority="high", status="completed")
    create_task(client, title="Update documentation", priority="low", status="pending")

    response = client.get(
        "/api/v1/tasks?priority=high&q=flask&page=1&per_page=1&sort_by=title&order=asc"
    )

    body = response.get_json()
    assert response.status_code == 200
    assert len(body["data"]) == 1
    assert body["data"][0]["title"] == "Deploy Flask API"
    assert body["meta"] == {
        "page": 1,
        "per_page": 1,
        "total": 1,
        "pages": 1,
        "has_next": False,
        "has_previous": False,
    }


def test_list_tasks_rejects_invalid_query_parameters(client: FlaskClient) -> None:
    response = client.get("/api/v1/tasks?page=0&status=blocked&sort_by=unknown&order=random")

    # Page validation runs before domain filter validation.
    assert response.status_code == 400
    assert response.get_json()["error"]["details"]["page"] == "Must be between 1 and 100000."

    response = client.get("/api/v1/tasks?status=blocked&sort_by=unknown&order=random")
    details = response.get_json()["error"]["details"]
    assert response.status_code == 400
    assert set(details) == {"status", "sort_by", "order"}


def test_get_task(client: FlaskClient) -> None:
    created = create_task(client)

    response = client.get(f"/api/v1/tasks/{created['id']}")

    assert response.status_code == 200
    assert response.get_json()["data"] == created


def test_get_missing_task_returns_404(client: FlaskClient) -> None:
    response = client.get("/api/v1/tasks/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == {
        "code": "not_found",
        "message": "Task 999 was not found.",
    }


def test_put_replaces_all_editable_fields(client: FlaskClient) -> None:
    created = create_task(
        client,
        description="Original description",
        status="completed",
        priority="high",
        due_date="2026-07-30",
    )

    response = client.put(
        f"/api/v1/tasks/{created['id']}",
        json={"title": "Replaced task"},
    )

    task = response.get_json()["data"]
    assert response.status_code == 200
    assert task["title"] == "Replaced task"
    assert task["description"] is None
    assert task["status"] == "pending"
    assert task["priority"] == "medium"
    assert task["due_date"] is None
    assert task["completed_at"] is None


def test_patch_updates_only_provided_fields(client: FlaskClient) -> None:
    created = create_task(client, priority="low", status="pending")

    response = client.patch(
        f"/api/v1/tasks/{created['id']}",
        json={"status": "completed", "priority": "high"},
    )

    task = response.get_json()["data"]
    assert response.status_code == 200
    assert task["title"] == created["title"]
    assert task["description"] == created["description"]
    assert task["status"] == "completed"
    assert task["priority"] == "high"
    assert task["completed_at"] is not None


def test_patch_rejects_empty_body(client: FlaskClient) -> None:
    created = create_task(client)

    response = client.patch(f"/api/v1/tasks/{created['id']}", json={})

    assert response.status_code == 400
    assert response.get_json()["error"]["details"]["body"] == (
        "At least one field must be provided."
    )


def test_delete_task(client: FlaskClient) -> None:
    created = create_task(client)

    response = client.delete(f"/api/v1/tasks/{created['id']}")

    assert response.status_code == 204
    assert response.data == b""
    assert client.get(f"/api/v1/tasks/{created['id']}").status_code == 404


def test_unknown_route_returns_json_error(client: FlaskClient) -> None:
    response = client.get("/unknown")

    assert response.status_code == 404
    assert response.is_json
    assert response.get_json()["error"]["code"] == "not_found"
