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
