def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = r.json()
    assert len(items) == 1


def test_list_action_items_filters_by_completed(client):
    r = client.post("/action-items/", json={"description": "Open one"})
    open_id = r.json()["id"]
    r = client.post("/action-items/", json={"description": "Done one"})
    done_id = r.json()["id"]
    client.put(f"/action-items/{done_id}/complete")

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert {item["id"] for item in r.json()} == {open_id, done_id}

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    items = r.json()
    assert {item["id"] for item in items} == {done_id}
    assert all(item["completed"] is True for item in items)

    r = client.get("/action-items/", params={"completed": "false"})
    assert r.status_code == 200
    items = r.json()
    assert {item["id"] for item in items} == {open_id}
    assert all(item["completed"] is False for item in items)


def test_bulk_complete_success(client):
    ids = []
    for i in range(3):
        r = client.post("/action-items/", json={"description": f"Task {i}"})
        ids.append(r.json()["id"])

    r = client.post("/action-items/bulk-complete", json={"ids": ids})
    assert r.status_code == 200, r.text
    items = r.json()
    assert {item["id"] for item in items} == set(ids)
    assert all(item["completed"] is True for item in items)

    r = client.get("/action-items/", params={"completed": "true"})
    assert {item["id"] for item in r.json()} == set(ids)


def test_bulk_complete_partial_failure_rolls_back_all(client):
    ids = []
    for i in range(2):
        r = client.post("/action-items/", json={"description": f"Task {i}"})
        ids.append(r.json()["id"])

    missing_id = max(ids) + 1000
    r = client.post("/action-items/bulk-complete", json={"ids": [*ids, missing_id]})
    assert r.status_code == 404

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = {item["id"]: item["completed"] for item in r.json()}
    for existing_id in ids:
        assert items[existing_id] is False
