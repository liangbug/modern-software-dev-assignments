def test_create_note_with_tags_and_manage_tags(client):
    r = client.post(
        "/notes/",
        json={"title": "Tagged", "content": "Body", "tag_names": ["work", "urgent", "work"]},
    )
    assert r.status_code == 201, r.text
    note = r.json()
    tag_names = {tag["name"] for tag in note["tags"]}
    assert tag_names == {"work", "urgent"}

    r = client.get("/tags/")
    assert r.status_code == 200
    assert {tag["name"] for tag in r.json()} == {"work", "urgent"}

    note_id = note["id"]
    r = client.post(f"/notes/{note_id}/tags/personal")
    assert r.status_code == 200
    tag_names = {tag["name"] for tag in r.json()["tags"]}
    assert tag_names == {"work", "urgent", "personal"}

    personal_tag_id = next(t["id"] for t in r.json()["tags"] if t["name"] == "personal")
    r = client.delete(f"/notes/{note_id}/tags/{personal_tag_id}")
    assert r.status_code == 200
    tag_names = {tag["name"] for tag in r.json()["tags"]}
    assert "personal" not in tag_names


def test_create_tag_is_idempotent_by_name(client):
    r = client.post("/tags/", json={"name": "shared"})
    assert r.status_code == 201
    first_id = r.json()["id"]

    r = client.post("/tags/", json={"name": "shared"})
    assert r.status_code == 201
    assert r.json()["id"] == first_id


def test_add_tag_to_missing_note_returns_404(client):
    r = client.post("/notes/999999/tags/x")
    assert r.status_code == 404
