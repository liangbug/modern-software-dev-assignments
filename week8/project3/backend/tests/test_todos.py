def test_list_empty(client):
    res = client.get("/api/todos")
    assert res.status_code == 200
    assert res.json() == []


def test_create_todo(client):
    res = client.post("/api/todos", json={"title": "買牛奶"})
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "買牛奶"
    assert body["completed"] is False

    res = client.get("/api/todos")
    assert len(res.json()) == 1


def test_create_todo_requires_title(client):
    res = client.post("/api/todos", json={"title": "  "})
    assert res.status_code == 422


def test_toggle_completed(client):
    created = client.post("/api/todos", json={"title": "寫作業"}).json()
    res = client.put(f"/api/todos/{created['id']}", json={"completed": True})
    assert res.status_code == 200
    assert res.json()["completed"] is True


def test_update_missing_todo(client):
    res = client.put("/api/todos/999", json={"completed": True})
    assert res.status_code == 404


def test_delete_todo(client):
    created = client.post("/api/todos", json={"title": "倒垃圾"}).json()
    res = client.delete(f"/api/todos/{created['id']}")
    assert res.status_code == 204

    res = client.get("/api/todos")
    assert res.json() == []


def test_delete_missing_todo(client):
    res = client.delete("/api/todos/999")
    assert res.status_code == 404
