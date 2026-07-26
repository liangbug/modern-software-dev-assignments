"""Tests for the search_papers and get_paper_detail MCP tools in main.py.

The @mcp.tool() decorator returns the original function unchanged, so these
call it directly as a coroutine -- no MCP client/transport needed. The
module-level ArxivClient is swapped for a mock-transport-backed one per test.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest
from mcp.server.fastmcp.exceptions import ToolError

import main
from arxiv_client import ArxivClient
from helpers import make_entry, make_feed


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def mock_arxiv(monkeypatch):
    """Yields a mutable {"handler": fn} so each test controls the mocked response."""
    state = {"handler": lambda request: httpx.Response(200, content=make_feed([]))}
    transport = httpx.MockTransport(lambda request: state["handler"](request))
    monkeypatch.setattr(main, "_client", ArxivClient(http_client=httpx.AsyncClient(transport=transport)))
    return state


def test_search_papers_returns_papers(mock_arxiv):
    mock_arxiv["handler"] = lambda request: httpx.Response(
        200, content=make_feed([make_entry(arxiv_id="2301.00001v1", title="Paper One")])
    )

    result = run(main.search_papers(query="cat:cs.AI"))

    assert result["query"] == "cat:cs.AI"
    assert result["count"] == 1
    assert result["papers"][0]["arxiv_id"] == "2301.00001v1"
    assert result["papers"][0]["title"] == "Paper One"


def test_search_papers_forwards_parameters(mock_arxiv):
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["params"] = dict(request.url.params)
        return httpx.Response(200, content=make_feed([]))

    mock_arxiv["handler"] = handler

    run(main.search_papers(query="ti:x", max_results=5, sort_by="submittedDate", sort_order="ascending"))

    assert captured["params"]["max_results"] == "5"
    assert captured["params"]["sortBy"] == "submittedDate"
    assert captured["params"]["sortOrder"] == "ascending"


def test_search_papers_no_matches_returns_message_not_error(mock_arxiv):
    mock_arxiv["handler"] = lambda request: httpx.Response(200, content=make_feed([]))

    result = run(main.search_papers(query="cat:zzz.nonexistent"))

    assert result["count"] == 0
    assert result["papers"] == []
    assert "message" in result


def test_search_papers_invalid_input_raises_tool_error(mock_arxiv):
    with pytest.raises(ToolError, match="non-empty string"):
        run(main.search_papers(query=""))


def test_get_paper_detail_returns_full_metadata(mock_arxiv):
    mock_arxiv["handler"] = lambda request: httpx.Response(
        200,
        content=make_feed(
            [make_entry(arxiv_id="2301.00001v1", comment="v1 notes", journal_ref="J. Example", doi="10.1000/x")]
        ),
    )

    result = run(main.get_paper_detail(arxiv_id="2301.00001v1"))

    assert result["arxiv_id"] == "2301.00001v1"
    assert result["categories"] == ["cs.AI", "cs.LG"]
    assert result["comment"] == "v1 notes"
    assert result["journal_ref"] == "J. Example"
    assert result["doi"] == "10.1000/x"


def test_get_paper_detail_unknown_id_raises_tool_error(mock_arxiv):
    mock_arxiv["handler"] = lambda request: httpx.Response(200, content=make_feed([]))

    with pytest.raises(ToolError, match="No paper found"):
        run(main.get_paper_detail(arxiv_id="9999.99999"))
