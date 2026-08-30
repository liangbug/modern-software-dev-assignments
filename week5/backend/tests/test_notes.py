def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) == {"items", "total", "page", "page_size"}

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_update_note(client):
    payload = {"title": "Original", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    updated = {"title": "Updated", "content": "Updated content"}
    r = client.put(f"/notes/{note_id}", json=updated)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "Updated"
    assert data["content"] == "Updated content"


def test_update_note_not_found(client):
    r = client.put("/notes/999999", json={"title": "X", "content": "Y"})
    assert r.status_code == 404


def test_delete_note(client):
    payload = {"title": "ToDelete", "content": "Bye"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404


def test_delete_note_not_found(client):
    r = client.delete("/notes/999999")
    assert r.status_code == 404


def test_create_note_validation_error_empty_title(client):
    r = client.post("/notes/", json={"title": "", "content": "Valid content"})
    assert r.status_code == 422


def test_create_note_validation_error_title_too_long(client):
    r = client.post("/notes/", json={"title": "x" * 201, "content": "Valid content"})
    assert r.status_code == 422


def test_create_note_validation_error_content_too_long(client):
    r = client.post("/notes/", json={"title": "Valid", "content": "x" * 5001})
    assert r.status_code == 422


def test_update_note_validation_error(client):
    payload = {"title": "Original", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "", "content": "Y"})
    assert r.status_code == 422
