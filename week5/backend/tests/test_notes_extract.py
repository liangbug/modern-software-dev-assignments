def test_extract_without_apply_does_not_write_action_items(client):
    # Use plain content (no hashtags) so note creation's own tag-sync side
    # effect doesn't interfere with asserting that /extract itself, without
    # apply=true, performs no DB writes.
    payload = {
        "title": "Trip planning",
        "content": "Plan trip\n- [ ] Book flights\n- [ ] Reserve hotel",
    }
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]
    assert r.json()["tags"] == []

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["tags"] == []
    assert data["action_items"] == ["Book flights", "Reserve hotel"]

    # No action items should have been created since apply was not set.
    r = client.get("/action-items/")
    assert r.json() == []


def test_extract_with_apply_true_persists_tags_and_action_items(client):
    payload = {
        "title": "Sprint notes",
        "content": "Sync with #backend team\n- [ ] Write extract endpoint\n- [ ] Add tests",
    }
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract", params={"apply": "true"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["tags"] == ["backend"]
    assert data["action_items"] == ["Write extract endpoint", "Add tests"]

    r = client.get(f"/notes/{note_id}")
    tag_names = {tag["name"] for tag in r.json()["tags"]}
    assert tag_names == {"backend"}

    r = client.get("/action-items/")
    descriptions = {item["description"] for item in r.json()}
    assert descriptions == {"Write extract endpoint", "Add tests"}


def test_extract_mixed_text_hashtags_checkboxes_and_legacy_markers(client):
    payload = {
        "title": "Mixed note",
        "content": (
            "Meeting notes #project #urgent\n"
            "- [ ] Follow up with client\n"
            "TODO: send invoice\n"
            "Ship it!\n"
            "Just a regular line, not actionable\n"
        ),
    }
    r = client.post("/notes/", json=payload)
    assert r.status_code == 201, r.text
    note_id = r.json()["id"]

    r = client.post(f"/notes/{note_id}/extract")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["tags"] == ["project", "urgent"]
    assert data["action_items"] == [
        "Follow up with client",
        "TODO: send invoice",
        "Ship it!",
    ]


def test_extract_note_not_found(client):
    r = client.post("/notes/999999/extract")
    assert r.status_code == 404
