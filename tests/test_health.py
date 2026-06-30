"""Tests for root and health-check routes."""

from flask.testing import FlaskClient


def test_index_returns_api_information(client: FlaskClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "name": "Flask Tasks CRUD API",
        "version": "1.0.0",
        "health": "/health",
        "tasks": "/api/v1/tasks",
    }


def test_health_check(client: FlaskClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "service": "flask-tasks-crud-api",
    }
