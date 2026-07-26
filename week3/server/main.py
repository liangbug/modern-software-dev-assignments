"""Arxiv Research MCP server.

Exposes two tools backed by the arXiv export API (https://arxiv.org/help/api):
- search_papers: find papers matching a topic/author/category query.
- get_paper_detail: fetch full metadata for one paper by its arXiv id.

Runs over STDIO, so all logging goes to stderr -- never stdout, which is
reserved for the JSON-RPC transport.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from arxiv_client import ArxivClient, ArxivClientError, PaperDetail, PaperSummary

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("arxiv_mcp")

mcp = FastMCP(
    name="arxiv-research",
    instructions=(
        "Search and inspect papers on arXiv. Call search_papers with a topic, "
        "author, or category query to find candidate papers, then call "
        "get_paper_detail with one of the returned arxiv_id values to fetch "
        "the full abstract and metadata."
    ),
    port=8003
)

_client = ArxivClient()


def _summary_to_dict(paper: PaperSummary) -> dict[str, Any]:
    return {
        "arxiv_id": paper.arxiv_id,
        "title": paper.title,
        "authors": paper.authors,
        "summary": paper.summary,
        "published": paper.published,
        "updated": paper.updated,
        "primary_category": paper.primary_category,
        "pdf_url": paper.pdf_url,
        "abs_url": paper.abs_url,
    }


@mcp.tool()
async def search_papers(
    query: str,
    max_results: int = 10,
    sort_by: str = "relevance",
    sort_order: str = "descending",
) -> dict[str, Any]:
    """Search arXiv for papers matching a query.

    Args:
        query: arXiv search query. Supports plain keywords ("diffusion models
            for protein folding") or field-qualified syntax
            ("ti:transformer AND cat:cs.CL").
        max_results: Number of results to return (1-50).
        sort_by: One of "relevance", "lastUpdatedDate", "submittedDate".
        sort_order: "ascending" or "descending".

    Returns:
        A dict with "query", "count", and "papers" -- each paper includes
        arxiv_id, title, authors, summary, published/updated dates,
        primary_category, pdf_url, and abs_url.
    """
    try:
        papers = await _client.search(
            query=query, max_results=max_results, sort_by=sort_by, sort_order=sort_order
        )
    except ArxivClientError as exc:
        raise ToolError(str(exc)) from exc

    if not papers:
        return {"query": query, "count": 0, "papers": [], "message": "No papers matched this query."}

    return {"query": query, "count": len(papers), "papers": [_summary_to_dict(p) for p in papers]}


@mcp.tool()
async def get_paper_detail(arxiv_id: str) -> dict[str, Any]:
    """Fetch full metadata for a single arXiv paper.

    Args:
        arxiv_id: The arXiv identifier, e.g. "2301.00001" or "2301.00001v2".
            Typically taken from the arxiv_id field returned by search_papers.

    Returns:
        A dict with title, authors, full abstract, all categories, comment,
        journal_ref, doi, pdf_url, and abs_url for the paper.
    """
    try:
        paper: PaperDetail = await _client.get_paper(arxiv_id)
    except ArxivClientError as exc:
        raise ToolError(str(exc)) from exc

    data = _summary_to_dict(paper)
    data.update(
        categories=paper.categories,
        comment=paper.comment,
        journal_ref=paper.journal_ref,
        doi=paper.doi,
    )
    return data


def main() -> None:
    logger.info("Starting arxiv-research MCP server over stdio")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
