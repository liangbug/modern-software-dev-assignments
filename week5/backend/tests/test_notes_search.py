def _create_note(client, title, content):
    r = client.post("/notes/", json={"title": title, "content": content})
    assert r.status_code == 201, r.text
    return r.json()["data"]


def test_search_no_results(client):
    _create_note(client, "Alpha", "First note")

    r = client.get("/notes/search/", params={"q": "nonexistent-keyword"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_search_empty_query_returns_all(client):
    _create_note(client, "Alpha", "First note")
    _create_note(client, "Beta", "Second note")

    r = client.get("/notes/search/")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_search_case_insensitive_title_and_content(client):
    _create_note(client, "Alpha Project", "notes about design")
    _create_note(client, "Beta Project", "ALPHA implementation details")
    _create_note(client, "Gamma", "unrelated content")

    r = client.get("/notes/search/", params={"q": "alpha"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 2
    titles = {item["title"] for item in data["items"]}
    assert titles == {"Alpha Project", "Beta Project"}


def test_search_pagination_across_pages(client):
    for i in range(1, 26):
        _create_note(client, f"Note {i:02d}", f"content {i}")

    r1 = client.get("/notes/search/", params={"page": 1, "page_size": 10})
    assert r1.status_code == 200
    data1 = r1.json()["data"]
    assert data1["total"] == 25
    assert data1["page"] == 1
    assert data1["page_size"] == 10
    assert len(data1["items"]) == 10

    r2 = client.get("/notes/search/", params={"page": 2, "page_size": 10})
    data2 = r2.json()["data"]
    assert data2["page"] == 2
    assert len(data2["items"]) == 10

    r3 = client.get("/notes/search/", params={"page": 3, "page_size": 10})
    data3 = r3.json()["data"]
    assert data3["page"] == 3
    assert len(data3["items"]) == 5

    ids_page1 = {item["id"] for item in data1["items"]}
    ids_page2 = {item["id"] for item in data2["items"]}
    ids_page3 = {item["id"] for item in data3["items"]}
    assert ids_page1.isdisjoint(ids_page2)
    assert ids_page2.isdisjoint(ids_page3)
    assert len(ids_page1 | ids_page2 | ids_page3) == 25


def test_search_sort_title_asc(client):
    _create_note(client, "Charlie", "c")
    _create_note(client, "Alpha", "a")
    _create_note(client, "Bravo", "b")

    r = client.get("/notes/search/", params={"sort": "title_asc"})
    assert r.status_code == 200
    titles = [item["title"] for item in r.json()["data"]["items"]]
    assert titles == sorted(titles)
    assert titles[:3] == ["Alpha", "Bravo", "Charlie"]


def test_search_sort_created_desc(client):
    first = _create_note(client, "First", "one")
    second = _create_note(client, "Second", "two")
    third = _create_note(client, "Third", "three")

    r = client.get("/notes/search/", params={"sort": "created_desc"})
    assert r.status_code == 200
    ids = [item["id"] for item in r.json()["data"]["items"]]
    assert ids == [third["id"], second["id"], first["id"]]
