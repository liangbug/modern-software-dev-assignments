from backend.app.services.extract import extract_action_items


def test_extract_action_items():
    text = """
    This is a note
    - TODO: write tests
    - ACTION: review PR
    - Ship it!
    Not actionable
    """.strip()
    items = extract_action_items(text)
    assert "TODO: write tests" in items
    assert "ACTION: review PR" in items
    assert "Ship it!" in items


def test_extract_action_items_checkboxes():
    text = """
    - [ ] write the report
    - [x] already done, should not appear
    - [X] also already done
    """.strip()
    items = extract_action_items(text)
    assert "write the report" in items
    assert "already done, should not appear" not in items
    assert "also already done" not in items


def test_extract_action_items_numbered_list():
    text = """
    1. Draft the proposal
    2) Send it to the client
    """.strip()
    items = extract_action_items(text)
    assert "Draft the proposal" in items
    assert "Send it to the client" in items


def test_extract_action_items_mentions_and_imperatives():
    text = """
    @bob please take a look at this
    Please review the pull request before Friday
    Schedule a meeting with the design team
    Just an FYI, nothing to do here
    """.strip()
    items = extract_action_items(text)
    assert "@bob please take a look at this" in items
    assert "Schedule a meeting with the design team" in items
    assert "Just an FYI, nothing to do here" not in items


def test_extract_action_items_dedupes():
    text = "TODO: same task\nTODO: same task"
    items = extract_action_items(text)
    assert items == ["TODO: same task"]
