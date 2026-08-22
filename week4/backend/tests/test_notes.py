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

    r = client.get("/notes/search/", params={"q": "Hello"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 1


def test_search_notes_is_case_insensitive(client):
    payload = {"title": "URGENT Reminder", "content": "please follow up soon"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text

    r = client.get("/notes/search/", params={"q": "urgent"})
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()]
    assert "URGENT Reminder" in titles

    r = client.get("/notes/search/", params={"q": "URGENT"})
    assert r.status_code == 200
    titles = [n["title"] for n in r.json()]
    assert "URGENT Reminder" in titles


def test_create_note_with_hashtags_returns_parsed_tags(client):
    payload = {"title": "Trip", "content": "Plan trip #urgent #followup rest of note"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["tags"] == ["urgent", "followup"]


def test_create_note_without_hashtags_returns_empty_tags(client):
    payload = {"title": "Plain", "content": "just a plain note without hashtags"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["tags"] == []


def test_get_note_returns_persisted_tags(client):
    payload = {"title": "Followup", "content": "remember to check #followup"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["tags"] == ["followup"]


def test_update_note_updates_title_and_content_and_reparses_tags(client):
    payload = {"title": "Old", "content": "Original content #old"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    update = {"title": "New", "content": "Updated content #new #followup"}
    r = client.put(f"/notes/{note_id}", json=update)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "New"
    assert data["content"] == "Updated content #new #followup"
    assert data["tags"] == ["new", "followup"]

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 200, r.text
    persisted = r.json()
    assert persisted["title"] == "New"
    assert persisted["content"] == "Updated content #new #followup"
    assert persisted["tags"] == ["new", "followup"]


def test_update_note_partial_title_only_keeps_content(client):
    payload = {"title": "Old", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "New"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["title"] == "New"
    assert data["content"] == "Original content"


def test_get_note_missing_id_returns_404(client):
    r = client.get("/notes/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"


def test_create_note_with_empty_title_returns_422(client):
    r = client.post("/notes/", json={"title": "", "content": "valid content"})
    assert r.status_code == 422

    r = client.get("/notes/")
    assert all(n["title"] != "" for n in r.json())


def test_create_note_with_empty_content_returns_422(client):
    r = client.post("/notes/", json={"title": "valid title", "content": ""})
    assert r.status_code == 422


def test_create_note_with_blank_title_returns_422(client):
    r = client.post("/notes/", json={"title": "   ", "content": "valid content"})
    assert r.status_code == 422


def test_create_note_with_blank_content_returns_422(client):
    r = client.post("/notes/", json={"title": "valid title", "content": "   "})
    assert r.status_code == 422


def test_update_note_with_blank_title_returns_422(client):
    payload = {"title": "Old", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"title": "   "})
    assert r.status_code == 422


def test_update_note_with_blank_content_returns_422(client):
    payload = {"title": "Old", "content": "Original content"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.put(f"/notes/{note_id}", json={"content": "   "})
    assert r.status_code == 422


def test_update_note_missing_id_returns_404(client):
    r = client.put("/notes/999999", json={"title": "New", "content": "New content"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"


def test_delete_note_removes_it(client):
    payload = {"title": "ToDelete", "content": "will be deleted"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204
    assert r.content == b""

    r = client.get(f"/notes/{note_id}")
    assert r.status_code == 404

    r = client.get("/notes/")
    assert all(n["id"] != note_id for n in r.json())


def test_delete_note_missing_id_returns_404(client):
    r = client.delete("/notes/999999")
    assert r.status_code == 404
    assert r.json()["detail"] == "Note not found"


def test_delete_note_does_not_affect_action_items(client):
    r = client.post("/action-items/", json={"description": "keep me"})
    assert r.status_code == 201, r.text
    action_item = r.json()

    r = client.post("/notes/", json={"title": "Independent", "content": "note content"})
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.delete(f"/notes/{note_id}")
    assert r.status_code == 204

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = {a["id"]: a for a in r.json()}
    assert action_item["id"] in items
    assert items[action_item["id"]]["description"] == action_item["description"]
    assert items[action_item["id"]]["completed"] == action_item["completed"]
