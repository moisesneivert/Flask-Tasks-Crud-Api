def test_create_task(client):
    response = client.post("/tasks", json={"title": "Test task"})
    assert response.status_code == 201

def test_list_tasks(client):
    response = client.get("/tasks")
    assert response.status_code == 200
