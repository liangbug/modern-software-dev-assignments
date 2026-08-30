def test_create_and_list_notes(client):
    payload = {"title": "Test", "content": "Hello world"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert data["title"] == "Test"

    r = client.get("/notes/")
    assert r.status_code == 200
    data = r.json()["data"]
    assert set(data.keys()) == {"items", "total"}
    assert len(data["items"]) >= 1

    r = client.get("/notes/search/")
    assert r.status_code == 200
    data = r.json()["data"]
    assert set(data.keys()) == {"items", "total", "page", "page_size"}

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_update_note(client):
    payload = {"title": "Original", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["data"]["id"]

    updated = {"title": "Updated", "content": "Updated content"}
    r = client.put(f"/notes/{note_id}", json=updated)
    assert r.status_code == 200, r.text
    data = r.json()["data"]
    assert data["title"] == "Updated"
    assert data["content"] == "Updated content"


def test_update_note_not_found(client):
    r = client.put("/notes/999999", json={"title": "X", "content": "Y"})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_delete_note(client):
    payload = {"title": "ToDelete", "content": "Bye"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["data"]["id"]

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
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


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
    note_id = r.json()["data"]["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "", "content": "Y"})
    assert r.status_code == 422


def test_list_notes_empty(client):
    r = client.get("/notes/")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data == {"items": [], "total": 0}


def test_list_notes_pagination_last_page_partial(client):
    for i in range(15):
        client.post("/notes/", json={"title": f"Note {i}", "content": "Body"})

    r = client.get("/notes/", params={"page": 2, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 15
    assert len(data["items"]) == 5


def test_list_notes_page_size_exceeds_total(client):
    for i in range(3):
        client.post("/notes/", json={"title": f"Note {i}", "content": "Body"})

    r = client.get("/notes/", params={"page": 1, "page_size": 50})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_list_notes_page_out_of_range_returns_empty_items(client):
    for i in range(3):
        client.post("/notes/", json={"title": f"Note {i}", "content": "Body"})

    r = client.get("/notes/", params={"page": 5, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 3
    assert data["items"] == []
