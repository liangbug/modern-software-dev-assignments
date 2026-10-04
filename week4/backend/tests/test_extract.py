from backend.app.services.extract import extract_action_items, extract_tags


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "Ship it!" in items


def test_extract_tags_multiple_distinct_tags():
    text = "Plan trip #urgent #followup rest of note"
    assert extract_tags(text) == ["urgent", "followup"]


def test_extract_tags_dedupes_repeated_tag():
    text = "#urgent something #urgent again"
    assert extract_tags(text) == ["urgent"]


def test_extract_tags_case_insensitive_dedup():
    text = "#Urgent later #urgent again"
    assert extract_tags(text) == ["urgent"]


def test_extract_tags_no_hashtags_returns_empty_list():
    text = "just a plain note without hashtags"
    assert extract_tags(text) == []


def test_extract_tags_bare_or_invalid_hash_not_counted():
    text = "broken tag: # and #! and # trailing"
    assert extract_tags(text) == []
