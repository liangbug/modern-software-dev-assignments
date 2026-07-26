"""Async client for the arXiv export API (https://arxiv.org/help/api).

Wraps the Atom-feed based search endpoint with:
- input validation
- a minimum delay between requests (arXiv asks for at most one request
  every ~3 seconds) plus retry/backoff on timeouts and transient errors
- Atom/XML parsing into plain dataclasses the MCP tools can serialize
"""

from __future__ import annotations

import asyncio
import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

import httpx

logger = logging.getLogger("arxiv_mcp.client")

ARXIV_API_URL = "https://export.arxiv.org/api/query"

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

MIN_REQUEST_INTERVAL_SECONDS = 3.0
REQUEST_TIMEOUT_SECONDS = 15.0
MAX_RETRIES = 3
VALID_SORT_BY = {"relevance", "lastUpdatedDate", "submittedDate"}
VALID_SORT_ORDER = {"ascending", "descending"}


class ArxivClientError(Exception):
    """A user-facing failure: bad input, no results, or an unreachable API."""


@dataclass
class PaperSummary:
    arxiv_id: str
    title: str
    authors: list[str]
    summary: str
    published: str
    updated: str
    primary_category: str
    pdf_url: str
    abs_url: str


@dataclass
class PaperDetail(PaperSummary):
    categories: list[str] = field(default_factory=list)
    comment: str | None = None
    journal_ref: str | None = None
    doi: str | None = None


def _text(node: ET.Element, path: str) -> str | None:
    child = node.find(path, NAMESPACES)
    if child is None or child.text is None:
        return None
    return " ".join(child.text.split())


def _parse_entry(entry: ET.Element, detailed: bool) -> PaperSummary | PaperDetail:
    raw_id = _text(entry, "atom:id") or ""
    arxiv_id = raw_id.rsplit("/", 1)[-1]

    authors = [_text(author, "atom:name") or "Unknown" for author in entry.findall("atom:author", NAMESPACES)]

    pdf_url = ""
    abs_url = raw_id
    for link in entry.findall("atom:link", NAMESPACES):
        if link.get("title") == "pdf":
            pdf_url = link.get("href", "")
        elif link.get("rel") == "alternate":
            abs_url = link.get("href", abs_url)

    primary_category_el = entry.find("arxiv:primary_category", NAMESPACES)
    primary_category = primary_category_el.get("term", "") if primary_category_el is not None else ""

    fields = dict(
        arxiv_id=arxiv_id,
        title=_text(entry, "atom:title") or "",
        authors=authors,
        summary=_text(entry, "atom:summary") or "",
        published=_text(entry, "atom:published") or "",
        updated=_text(entry, "atom:updated") or "",
        primary_category=primary_category,
        pdf_url=pdf_url,
        abs_url=abs_url,
    )

    if not detailed:
        return PaperSummary(**fields)

    return PaperDetail(
        **fields,
        categories=[cat.get("term", "") for cat in entry.findall("atom:category", NAMESPACES)],
        comment=_text(entry, "arxiv:comment"),
        journal_ref=_text(entry, "arxiv:journal_ref"),
        doi=_text(entry, "arxiv:doi"),
    )


class ArxivClient:
    """Rate-limited async wrapper around the arXiv Atom search API."""

    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self._client = http_client or httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS)
        self._owns_client = http_client is None
        self._lock = asyncio.Lock()
        self._last_request_at = 0.0

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def _get(self, params: dict) -> ET.Element:
        async with self._lock:
            wait = MIN_REQUEST_INTERVAL_SECONDS - (time.monotonic() - self._last_request_at)
            if wait > 0:
                await asyncio.sleep(wait)

            last_error: Exception | None = None
            for attempt in range(1, MAX_RETRIES + 1):
                try:
                    response = await self._client.get(ARXIV_API_URL, params=params)
                    response.raise_for_status()
                    self._last_request_at = time.monotonic()
                    return ET.fromstring(response.content)
                except httpx.TimeoutException as exc:
                    last_error = exc
                    logger.warning("arXiv request timed out (attempt %d/%d)", attempt, MAX_RETRIES)
                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    if status == 429 or 500 <= status < 600:
                        last_error = exc
                        logger.warning("arXiv returned %d (attempt %d/%d)", status, attempt, MAX_RETRIES)
                    else:
                        raise ArxivClientError(
                            f"arXiv API rejected the request ({status}). Check the query syntax or id."
                        ) from exc
                except httpx.HTTPError as exc:
                    last_error = exc
                    logger.warning("arXiv request failed (attempt %d/%d): %s", attempt, MAX_RETRIES, exc)

                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** (attempt - 1))

            raise ArxivClientError(
                "Could not reach the arXiv API after several attempts. Please try again shortly."
            ) from last_error

    async def search(
        self,
        query: str,
        max_results: int = 10,
        sort_by: str = "relevance",
        sort_order: str = "descending",
    ) -> list[PaperSummary]:
        if not query or not query.strip():
            raise ArxivClientError("query must be a non-empty string.")
        if not 1 <= max_results <= 50:
            raise ArxivClientError("max_results must be between 1 and 50.")
        if sort_by not in VALID_SORT_BY:
            raise ArxivClientError(f"sort_by must be one of: {', '.join(sorted(VALID_SORT_BY))}.")
        if sort_order not in VALID_SORT_ORDER:
            raise ArxivClientError(f"sort_order must be one of: {', '.join(sorted(VALID_SORT_ORDER))}.")

        root = await self._get(
            {
                "search_query": query,
                "start": 0,
                "max_results": max_results,
                "sortBy": sort_by,
                "sortOrder": sort_order,
            }
        )
        return [_parse_entry(entry, detailed=False) for entry in root.findall("atom:entry", NAMESPACES)]

    async def get_paper(self, arxiv_id: str) -> PaperDetail:
        arxiv_id = (arxiv_id or "").strip()
        if not arxiv_id:
            raise ArxivClientError("arxiv_id must be a non-empty string.")

        root = await self._get({"id_list": arxiv_id, "max_results": 1})
        entries = root.findall("atom:entry", NAMESPACES)
        if not entries:
            raise ArxivClientError(f"No paper found on arXiv for id '{arxiv_id}'.")

        entry = entries[0]
        entry_id = _text(entry, "atom:id") or ""
        if entry_id.startswith("http://arxiv.org/api/errors"):
            reason = _text(entry, "atom:summary") or "unknown error"
            raise ArxivClientError(f"arXiv could not resolve id '{arxiv_id}': {reason}")

        return _parse_entry(entry, detailed=True)
