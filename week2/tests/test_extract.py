import json
import os
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def _mock_chat_response(items):
    return SimpleNamespace(message=SimpleNamespace(content=json.dumps(items)))


@patch.dict(os.environ, {"GEMINI_MODEL": "gemini-test-model"})
@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_bullets(mock_chat):
    mock_chat.return_value = _mock_chat_response(
        ["Set up database", "implement API extract endpoint", "Write tests"]
    )
    text = """
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    """.strip()

    items = extract_action_items_llm(text)

    assert items == ["Set up database", "implement API extract endpoint", "Write tests"]
    mock_chat.assert_called_once()
    called_model, called_messages = mock_chat.call_args.args[:2]
    assert called_model == "gemini-test-model"
    assert called_messages[0]["role"] == "system"
    assert called_messages[1] == {"role": "user", "content": text}


@patch.dict(os.environ, {"GEMINI_MODEL": "gemini-test-model"})
@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_keyword_prefixes(mock_chat):
    mock_chat.return_value = _mock_chat_response(
        ["Deploy to staging", "Review pull request", "Prepare demo"]
    )
    text = """
    todo: Deploy to staging
    action: Review pull request
    next: Prepare demo
    """.strip()

    items = extract_action_items_llm(text)

    assert items == ["Deploy to staging", "Review pull request", "Prepare demo"]


@patch.dict(os.environ, {"GEMINI_MODEL": "gemini-test-model"})
@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_empty_input(mock_chat):
    mock_chat.return_value = _mock_chat_response([])

    items = extract_action_items_llm("")

    assert items == []


@patch.dict(os.environ, {"GEMINI_MODEL": "gemini-test-model"})
@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_invalid_json(mock_chat):
    mock_chat.return_value = SimpleNamespace(message=SimpleNamespace(content="not json"))

    items = extract_action_items_llm("some text")

    assert items == []


@pytest.mark.skipif(
    not os.environ.get("GEMINI_API_KEY") or not os.environ.get("GEMINI_MODEL"),
    reason="GEMINI_API_KEY or GEMINI_MODEL not set, skip real Gemini API integration test",
)
def test_extract_action_items_llm_real_api():
    text = """
    Meeting notes:
    - [ ] Set up database
    todo: Deploy to staging
    next: Prepare demo
    Some narrative sentence with no action.
    """.strip()

    items = extract_action_items_llm(text)

    assert isinstance(items, list)
    assert len(items) > 0
    assert all(isinstance(item, str) for item in items)
