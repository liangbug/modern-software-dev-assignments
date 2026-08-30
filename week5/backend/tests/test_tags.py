def test_create_note_with_hashtags_auto_creates_and_attaches_tags(client):
    payload = {"title": "Groceries", "content": "Buy milk #shopping #home"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    tag_names = {t["name"] for t in data["tags"]}
    assert tag_names == {"shopping", "home"}


def test_duplicate_hashtags_do_not_create_duplicate_tags(client):
    payload = {"title": "Note1", "content": "Task #work #work"}
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert len(data["tags"]) == 1

    payload2 = {"title": "Note2", "content": "Another #work item"}
    r = client.post("/notes/", json=payload2)
    assert r.status_code == 201, r.text

    r = client.get("/tags")
    assert r.status_code == 200
    work_tags = [t for t in r.json()["data"] if t["name"].lower() == "work"]
    assert len(work_tags) == 1


def test_create_and_list_tags(client):
    r = client.post("/tags", json={"name": "urgent"})
    assert r.status_code == 201, r.text
    tag = r.json()["data"]
    assert tag["name"] == "urgent"

    # Creating the same tag name again should reuse the existing tag.
    r = client.post("/tags", json={"name": "urgent"})
    assert r.status_code == 201, r.text
    assert r.json()["data"]["id"] == tag["id"]

    r = client.get("/tags")
    assert r.status_code == 200
    assert len([t for t in r.json()["data"] if t["name"] == "urgent"]) == 1


def test_attach_and_detach_tag_on_note(client):
    r = client.post("/notes/", json={"title": "Plain", "content": "No hashtags here"})
    note_id = r.json()["data"]["id"]
    assert r.json()["data"]["tags"] == []

    r = client.post(f"/notes/{note_id}/tags", json={"name": "important"})
    assert r.status_code == 201, r.text
    data = r.json()["data"]
    assert [t["name"] for t in data["tags"]] == ["important"]
    tag_id = data["tags"][0]["id"]

    # Attaching the same tag again should not create a duplicate association.
    r = client.post(f"/notes/{note_id}/tags", json={"name": "important"})
    assert r.status_code == 201, r.text
    assert len(r.json()["data"]["tags"]) == 1

    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 200, r.text
    assert r.json()["data"]["tags"] == []


def test_detach_tag_not_attached_returns_404(client):
    r = client.post("/notes/", json={"title": "Plain", "content": "No hashtags"})
    note_id = r.json()["data"]["id"]

    r = client.post("/tags", json={"name": "unrelated"})
    tag_id = r.json()["data"]["id"]

    r = client.delete(f"/notes/{note_id}/tags/{tag_id}")
    assert r.status_code == 404


def test_delete_tag_not_found(client):
    r = client.delete("/tags/999999")
    assert r.status_code == 404


def test_delete_tag_removes_association(client):
    r = client.post("/notes/", json={"title": "Note", "content": "Text #removable"})
    note = r.json()["data"]
    tag_id = note["tags"][0]["id"]

    r = client.delete(f"/tags/{tag_id}")
    assert r.status_code == 204

    r = client.get(f"/notes/{note['id']}")
    assert r.status_code == 200
    assert r.json()["data"]["tags"] == []


def test_filter_notes_by_tag(client):
    client.post("/notes/", json={"title": "A", "content": "About #python"})
    client.post("/notes/", json={"title": "B", "content": "About #golang"})
    client.post("/notes/", json={"title": "C", "content": "Also #python related"})

    r = client.get("/notes/", params={"tag": "python"})
    assert r.status_code == 200
    titles = {n["title"] for n in r.json()["data"]}
    assert titles == {"A", "C"}

    r = client.get("/notes/search/", params={"tag": "golang"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["title"] == "B"
