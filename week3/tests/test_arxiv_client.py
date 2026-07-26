"""Unit tests for ArxivClient. All HTTP calls go through httpx.MockTransport, so these
run offline and never hit the real arXiv API.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

import arxiv_client as arxiv_client_module
from arxiv_client import ArxivClient, ArxivClientError
from helpers import make_entry, make_error_entry, make_feed


def run(coro):
    return asyncio.run(coro)


async def _instant_sleep(_seconds: float) -> None:
    return None


def client_with_handler(handler) -> ArxivClient:
    transport = httpx.MockTransport(handler)
    return ArxivClient(http_client=httpx.AsyncClient(transport=transport))


def test_search_returns_parsed_papers():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        feed = make_feed(
            [
                make_entry(arxiv_id="2301.00001v1", title="Paper One"),
                make_entry(arxiv_id="2301.00002v1", title="Paper Two"),
            ]
        )
        return httpx.Response(200, content=feed)

    papers = run(client_with_handler(handler).search("cat:cs.AI", max_results=2))

    assert len(calls) == 1
    assert calls[0].url.params["search_query"] == "cat:cs.AI"
    assert [p.title for p in papers] == ["Paper One", "Paper Two"]
    assert papers[0].arxiv_id == "2301.00001v1"
    assert papers[0].authors == ["Jane Doe", "John Smith"]
    assert papers[0].primary_category == "cs.AI"
    assert papers[0].pdf_url == "http://arxiv.org/pdf/2301.00001v1"
    assert papers[0].abs_url == "http://arxiv.org/abs/2301.00001v1"


def test_search_forwards_sort_parameters():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["params"] = dict(request.url.params)
        return httpx.Response(200, content=make_feed([]))

    run(client_with_handler(handler).search("ti:x", max_results=5, sort_by="submittedDate", sort_order="ascending"))

    assert captured["params"]["max_results"] == "5"
    assert captured["params"]["sortBy"] == "submittedDate"
    assert captured["params"]["sortOrder"] == "ascending"


def test_search_empty_results_returns_empty_list():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=make_feed([]))

    papers = run(client_with_handler(handler).search("cat:zzz.nonexistent"))
    assert papers == []


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"query": ""}, "query must be a non-empty string"),
        ({"query": "   "}, "query must be a non-empty string"),
        ({"query": "x", "max_results": 0}, "max_results must be between 1 and 50"),
        ({"query": "x", "max_results": 51}, "max_results must be between 1 and 50"),
        ({"query": "x", "sort_by": "bogus"}, "sort_by must be one of"),
        ({"query": "x", "sort_order": "bogus"}, "sort_order must be one of"),
    ],
)
def test_search_rejects_invalid_input_without_calling_api(kwargs, message):
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, content=make_feed([]))

    with pytest.raises(ArxivClientError, match=message):
        run(client_with_handler(handler).search(**kwargs))
    assert called is False


def test_get_paper_returns_full_detail():
    def handler(request: httpx.Request) -> httpx.Response:
        entry = make_entry(
            arxiv_id="2301.00001v1",
            categories=("cs.AI", "cs.LG"),
            comment="10 pages, 3 figures",
            journal_ref="Nature 2023",
            doi="10.1000/example",
        )
        return httpx.Response(200, content=make_feed([entry]))

    paper = run(client_with_handler(handler).get_paper("2301.00001v1"))

    assert paper.title == "Sample Paper Title"
    assert paper.categories == ["cs.AI", "cs.LG"]
    assert paper.comment == "10 pages, 3 figures"
    assert paper.journal_ref == "Nature 2023"
    assert paper.doi == "10.1000/example"


def test_get_paper_not_found_when_feed_is_empty():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=make_feed([]))

    with pytest.raises(ArxivClientError, match="No paper found"):
        run(client_with_handler(handler).get_paper("9999.99999"))


def test_get_paper_surfaces_arxiv_error_entry():
    def handler(request: httpx.Request) -> httpx.Response:
        entry = make_error_entry("not-a-real-id", "incorrect id format for not-a-real-id")
        return httpx.Response(200, content=make_feed([entry]))

    with pytest.raises(ArxivClientError, match="incorrect id format"):
        run(client_with_handler(handler).get_paper("not-a-real-id"))


def test_get_paper_rejects_blank_id_without_calling_api():
    called = False

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal called
        called = True
        return httpx.Response(200, content=make_feed([]))

    with pytest.raises(ArxivClientError, match="arxiv_id must be a non-empty string"):
        run(client_with_handler(handler).get_paper("   "))
    assert called is False


def test_retries_on_server_error_then_succeeds(monkeypatch):
    monkeypatch.setattr(arxiv_client_module.asyncio, "sleep", _instant_sleep)
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] < 2:
            return httpx.Response(503, text="temporarily unavailable")
        return httpx.Response(200, content=make_feed([make_entry()]))

    papers = run(client_with_handler(handler).search("cat:cs.AI"))

    assert attempts["count"] == 2
    assert len(papers) == 1


def test_raises_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr(arxiv_client_module.asyncio, "sleep", _instant_sleep)
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(500, text="server error")

    with pytest.raises(ArxivClientError, match="Could not reach the arXiv API"):
        run(client_with_handler(handler).search("cat:cs.AI"))

    assert attempts["count"] == arxiv_client_module.MAX_RETRIES


def test_non_retryable_error_fails_fast(monkeypatch):
    monkeypatch.setattr(arxiv_client_module.asyncio, "sleep", _instant_sleep)
    attempts = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        return httpx.Response(400, text="bad request")

    with pytest.raises(ArxivClientError, match="rejected the request"):
        run(client_with_handler(handler).search("cat:cs.AI"))

    assert attempts["count"] == 1
