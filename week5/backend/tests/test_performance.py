from sqlalchemy import text


def _seed_notes(client, count):
    for i in range(count):
        client.post("/notes/", json={"title": f"Note {i:04d}", "content": f"Body #tag{i % 5} {i}"})


def test_large_dataset_search_pagination_stays_correct(client):
    _seed_notes(client, 300)

    r = client.get("/notes/search/", params={"page": 5, "page_size": 20, "sort": "title_asc"})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 300
    assert len(data["items"]) == 20
    titles = [item["title"] for item in data["items"]]
    assert titles == sorted(titles)

    r = client.get("/notes/search/", params={"tag": "tag2", "page": 1, "page_size": 500})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 60


def test_notes_title_index_used_in_query_plan(db_session):
    plan = db_session.execute(
        text("EXPLAIN QUERY PLAN SELECT * FROM notes WHERE title = 'x' ORDER BY title ASC")
    ).all()
    plan_text = " ".join(str(row) for row in plan)
    assert "ix_notes_title" in plan_text


def test_note_tags_tag_id_index_used_in_query_plan(db_session):
    plan = db_session.execute(
        text("EXPLAIN QUERY PLAN SELECT * FROM note_tags WHERE tag_id = 1")
    ).all()
    plan_text = " ".join(str(row) for row in plan)
    assert "ix_note_tags_tag_id" in plan_text
