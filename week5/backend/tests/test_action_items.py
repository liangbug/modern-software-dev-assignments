def test_create_and_complete_action_item(client):
    payload = {"description": "Ship it"}
    r = client.post("/action-items/", json=payload)
    assert r.status_code == 201, r.text
    item = r.json()["data"]
    assert item["completed"] is False

    r = client.put(f"/action-items/{item['id']}/complete")
    assert r.status_code == 200
    done = r.json()["data"]
    assert done["completed"] is True

    r = client.get("/action-items/")
    assert r.status_code == 200
    data = r.json()["data"]
    assert set(data.keys()) == {"items", "total"}
    assert data["total"] == 1
    assert len(data["items"]) == 1


def test_list_action_items_filters_by_completed(client):
    r = client.post("/action-items/", json={"description": "Open one"})
    open_id = r.json()["data"]["id"]
    r = client.post("/action-items/", json={"description": "Done one"})
    done_id = r.json()["data"]["id"]
    client.put(f"/action-items/{done_id}/complete")

    r = client.get("/action-items/")
    assert r.status_code == 200
    assert {item["id"] for item in r.json()["data"]["items"]} == {open_id, done_id}

    r = client.get("/action-items/", params={"completed": "true"})
    assert r.status_code == 200
    data = r.json()["data"]
    items = data["items"]
    assert data["total"] == 1
    assert {item["id"] for item in items} == {done_id}
    assert all(item["completed"] is True for item in items)

    r = client.get("/action-items/", params={"completed": "false"})
    assert r.status_code == 200
    data = r.json()["data"]
    items = data["items"]
    assert data["total"] == 1
    assert {item["id"] for item in items} == {open_id}
    assert all(item["completed"] is False for item in items)


def test_bulk_complete_success(client):
    ids = []
    for i in range(3):
        r = client.post("/action-items/", json={"description": f"Task {i}"})
        ids.append(r.json()["data"]["id"])

    r = client.post("/action-items/bulk-complete", json={"ids": ids})
    assert r.status_code == 200, r.text
    items = r.json()["data"]
    assert {item["id"] for item in items} == set(ids)
    assert all(item["completed"] is True for item in items)

    r = client.get("/action-items/", params={"completed": "true"})
    assert {item["id"] for item in r.json()["data"]["items"]} == set(ids)


def test_bulk_complete_partial_failure_rolls_back_all(client):
    ids = []
    for i in range(2):
        r = client.post("/action-items/", json={"description": f"Task {i}"})
        ids.append(r.json()["data"]["id"])

    missing_id = max(ids) + 1000
    r = client.post("/action-items/bulk-complete", json={"ids": [*ids, missing_id]})
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"

    r = client.get("/action-items/")
    assert r.status_code == 200
    items = {item["id"]: item["completed"] for item in r.json()["data"]["items"]}
    for existing_id in ids:
        assert items[existing_id] is False


def test_list_action_items_empty(client):
    r = client.get("/action-items/")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data == {"items": [], "total": 0}


def test_list_action_items_pagination_last_page_partial(client):
    for i in range(15):
        client.post("/action-items/", json={"description": f"Task {i}"})

    r = client.get("/action-items/", params={"page": 2, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 15
    assert len(data["items"]) == 5


def test_list_action_items_page_size_exceeds_total(client):
    for i in range(3):
        client.post("/action-items/", json={"description": f"Task {i}"})

    r = client.get("/action-items/", params={"page": 1, "page_size": 50})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 3
    assert len(data["items"]) == 3


def test_create_action_item_validation_error_empty_description(client):
    r = client.post("/action-items/", json={"description": ""})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "VALIDATION_ERROR"


def test_complete_action_item_not_found(client):
    r = client.put("/action-items/999999/complete")
    assert r.status_code == 404
    assert r.json()["error"]["code"] == "NOT_FOUND"


def test_bulk_complete_concurrent_disjoint_batches_are_consistent(client):
    import concurrent.futures

    batch_a = []
    batch_b = []
    for i in range(10):
        r = client.post("/action-items/", json={"description": f"A{i}"})
        batch_a.append(r.json()["data"]["id"])
    for i in range(10):
        r = client.post("/action-items/", json={"description": f"B{i}"})
        batch_b.append(r.json()["data"]["id"])

    def complete(ids):
        return client.post("/action-items/bulk-complete", json={"ids": ids})

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(complete, batch_a), pool.submit(complete, batch_b)]
        results = [f.result() for f in futures]

    assert all(r.status_code == 200 for r in results)

    r = client.get("/action-items/", params={"completed": "true", "page_size": 50})
    completed_ids = {item["id"] for item in r.json()["data"]["items"]}
    assert completed_ids == set(batch_a) | set(batch_b)


def test_list_action_items_page_out_of_range_returns_empty_items(client):
    for i in range(3):
        client.post("/action-items/", json={"description": f"Task {i}"})

    r = client.get("/action-items/", params={"page": 5, "page_size": 10})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 3
    assert data["items"] == []
