def _create_notes(client, count: int) -> list[dict]:
    return [
        client.post("/notes/", json={"title": f"Note {i}", "content": f"Body {i}"}).json()
        for i in range(count)
    ]


def _create_action_items(client, count: int) -> list[dict]:
    return [
        client.post("/action-items/", json={"description": f"Item {i}"}).json()
        for i in range(count)
    ]


def test_notes_pagination_skip_and_limit(client):
    _create_notes(client, 5)

    r = client.get("/notes/", params={"limit": 2, "skip": 0, "sort": "id"})
    assert r.status_code == 200
    page1 = r.json()
    assert [n["title"] for n in page1] == ["Note 0", "Note 1"]

    r = client.get("/notes/", params={"limit": 2, "skip": 2, "sort": "id"})
    page2 = r.json()
    assert [n["title"] for n in page2] == ["Note 2", "Note 3"]

    r = client.get("/notes/", params={"limit": 2, "skip": 4, "sort": "id"})
    page3 = r.json()
    assert [n["title"] for n in page3] == ["Note 4"]

    all_ids = [n["id"] for n in page1 + page2 + page3]
    assert len(all_ids) == len(set(all_ids)) == 5


def test_notes_sort_ascending_and_descending(client):
    _create_notes(client, 3)

    r = client.get("/notes/", params={"sort": "title", "limit": 10})
    titles_asc = [n["title"] for n in r.json() if n["title"].startswith("Note")]
    assert titles_asc == sorted(titles_asc)

    r = client.get("/notes/", params={"sort": "-title", "limit": 10})
    titles_desc = [n["title"] for n in r.json() if n["title"].startswith("Note")]
    assert titles_desc == sorted(titles_desc, reverse=True)


def test_notes_sort_falls_back_to_created_at_for_unknown_field(client):
    _create_notes(client, 2)

    r = client.get("/notes/", params={"sort": "not_a_real_field", "limit": 10})
    assert r.status_code == 200
    ids = [n["id"] for n in r.json()]
    assert ids == sorted(ids, reverse=True)


def test_notes_limit_is_capped_at_200(client):
    r = client.get("/notes/", params={"limit": 500})
    assert r.status_code == 422


def test_action_items_pagination_skip_and_limit(client):
    _create_action_items(client, 5)

    r = client.get("/action-items/", params={"limit": 2, "skip": 0, "sort": "id"})
    page1 = r.json()
    assert [i["description"] for i in page1] == ["Item 0", "Item 1"]

    r = client.get("/action-items/", params={"limit": 2, "skip": 2, "sort": "id"})
    page2 = r.json()
    assert [i["description"] for i in page2] == ["Item 2", "Item 3"]


def test_action_items_sort_ascending_and_descending(client):
    _create_action_items(client, 3)

    r = client.get("/action-items/", params={"sort": "description", "limit": 10})
    descriptions_asc = [i["description"] for i in r.json() if i["description"].startswith("Item")]
    assert descriptions_asc == sorted(descriptions_asc)

    r = client.get("/action-items/", params={"sort": "-description", "limit": 10})
    descriptions_desc = [i["description"] for i in r.json() if i["description"].startswith("Item")]
    assert descriptions_desc == sorted(descriptions_desc, reverse=True)


def test_action_items_filter_by_completed_with_pagination(client):
    items = _create_action_items(client, 4)
    client.put(f"/action-items/{items[0]['id']}/complete")
    client.put(f"/action-items/{items[2]['id']}/complete")

    r = client.get("/action-items/", params={"completed": True, "sort": "id", "limit": 10})
    completed_ids = {i["id"] for i in r.json()}
    assert completed_ids == {items[0]["id"], items[2]["id"]}

    r = client.get("/action-items/count", params={"completed": True})
    assert r.json()["count"] == 2
