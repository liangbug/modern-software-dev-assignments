from backend.app.services.extract import extract_action_items, extract_hashtags


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


def test_extract_hashtags_dedupes_case_insensitively_preserving_order():
    text = "Plan trip #Travel and #food, also #travel again"
    tags = extract_hashtags(text)
    assert tags == ["Travel", "food"]


def test_extract_hashtags_no_hashtags_returns_empty_list():
    assert extract_hashtags("No tags in this text.") == []
