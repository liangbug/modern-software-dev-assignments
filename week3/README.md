# Arxiv Research MCP Server

A local (STDIO) MCP server that wraps the [arXiv export API](https://arxiv.org/help/api)
so an MCP client (Claude Desktop, Cursor, etc.) can search papers and pull full
metadata for a specific paper.

## Tools

### `search_papers`

Search arXiv for papers matching a query.

| Parameter    | Type   | Required | Default       | Notes                                                              |
|--------------|--------|----------|---------------|---------------------------------------------------------------------|
| `query`      | string | yes      | —             | Plain keywords or arXiv field syntax, e.g. `ti:transformer AND cat:cs.CL` |
| `max_results`| int    | no       | `10`          | 1–50                                                                 |
| `sort_by`    | string | no       | `relevance`   | `relevance` \| `lastUpdatedDate` \| `submittedDate`                  |
| `sort_order` | string | no       | `descending`  | `ascending` \| `descending`                                         |

Example call:

```json
{ "query": "diffusion models for protein folding", "max_results": 3 }
```

Example output (truncated):

```json
{
  "query": "diffusion models for protein folding",
  "count": 3,
  "papers": [
    {
      "arxiv_id": "2307.01189v2",
      "title": "Trainable Transformer in Transformer",
      "authors": ["Abhishek Panigrahi", "..."],
      "summary": "Recent works attribute the capability of in-context learning ...",
      "published": "2023-07-03T17:53:39Z",
      "updated": "2024-02-08T16:19:14Z",
      "primary_category": "cs.CL",
      "pdf_url": "https://arxiv.org/pdf/2307.01189v2",
      "abs_url": "https://arxiv.org/abs/2307.01189v2"
    }
  ]
}
```

If nothing matches, `count` is `0` and `papers` is an empty list with a
`message` explaining no results were found (never an error).

### `get_paper_detail`

Fetch full metadata for one paper.

| Parameter  | Type   | Required | Notes                                                    |
|------------|--------|----------|-----------------------------------------------------------|
| `arxiv_id` | string | yes      | e.g. `2301.00001` or `2301.00001v2` (usually copied from a `search_papers` result) |

Example call:

```json
{ "arxiv_id": "2307.01189v2" }
```

Example output (truncated):

```json
{
  "arxiv_id": "2307.01189v2",
  "title": "Trainable Transformer in Transformer",
  "authors": ["Abhishek Panigrahi", "Sadhika Malladi", "Mengzhou Xia", "Sanjeev Arora"],
  "summary": "Recent works attribute the capability of in-context learning ...",
  "published": "2023-07-03T17:53:39Z",
  "updated": "2024-02-08T16:19:14Z",
  "primary_category": "cs.CL",
  "pdf_url": "https://arxiv.org/pdf/2307.01189v2",
  "abs_url": "https://arxiv.org/abs/2307.01189v2",
  "categories": ["cs.CL", "cs.LG"],
  "comment": null,
  "journal_ref": null,
  "doi": null
}
```

If the id doesn't resolve to a real paper, the tool returns an MCP tool error
(`isError: true`) with a message like `No paper found on arXiv for id '...'.`
instead of a stack trace.

## Resilience

- **Input validation**: empty queries, out-of-range `max_results`, and invalid
  `sort_by`/`sort_order` values are rejected before any HTTP call, with a
  clear message.
- **Rate limiting**: arXiv asks clients not to exceed one request every ~3
  seconds — the client enforces a minimum 3s gap between outgoing requests
  via an internal lock, regardless of how fast tool calls come in.
- **Timeouts & transient errors**: requests use a 15s timeout and retry up to
  3 times with exponential backoff on timeouts, 429s, and 5xx responses.
  Non-retryable errors (e.g. a malformed query) fail fast with the arXiv
  response status.
- **Empty results**: a search with no matches returns a normal (non-error)
  response with `count: 0`, not an exception.
- **Logging**: all logs go to `stderr` via the standard `logging` module —
  `stdout` is reserved for the STDIO JSON-RPC transport.

## Prerequisites

- Python >= 3.10
- [`uv`](https://docs.astral.sh/uv/) (dependencies for this server are
  declared in the repo root `pyproject.toml` under the `week3` dependency
  group: `mcp`, `httpx`)

## Setup

From the repository root:

```bash
uv sync --group week3
```

## Run it directly (for a quick smoke test)

The server speaks MCP over stdio, so running it directly just waits for a
JSON-RPC client on stdin — that's expected, not a hang:

```bash
cd week3/server
uv run --project ../.. --group week3 python main.py
```

`--project ../..` tells uv where to find the repo root's `pyproject.toml`/
`uv.lock` (which declare the `week3` dependency group), without changing
the working directory `main.py` runs in. Equivalently, from the repo root:

```bash
uv run --group week3 python week3/server/main.py
```

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to
exercise it interactively without wiring up a full client:

```bash
npx @modelcontextprotocol/inspector uv run --group week3 python week3/server/main.py
```

## Run tests

Unit tests cover both tools (`search_papers`, `get_paper_detail`) and the
underlying `ArxivClient` (parsing, validation, retries/backoff, rate-limit
timing) using `httpx.MockTransport` — no network access, no real 3s delays:

```bash
uv run --group week3 pytest week3/tests -q
```

## Configure Claude Desktop

Add this server to your Claude Desktop config
(`claude_desktop_config.json` — on Windows:
`%APPDATA%\Claude\claude_desktop_config.json`; on macOS:
`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "arxiv-research": {
      "command": "uv",
      "args": [
        "run",
        "--group", "week3",
        "--directory", "C:/code/modern-software-dev-assignments/modern-software-dev-assignments-light/week3/server",
        "python",
        "main.py"
      ]
    }
  }
}
```

Restart Claude Desktop, then look for the hammer/tools icon to confirm
`search_papers` and `get_paper_detail` are listed under **arxiv-research**.

## Example invocation flow

1. In Claude Desktop, type: *"Find recent arXiv papers on linear attention
   transformers."* Claude calls `search_papers` with something like
   `{"query": "ti:linear attention AND cat:cs.LG", "max_results": 5}` and
   summarizes the returned titles/abstracts.
2. Follow up with: *"Tell me more about the second one, including its
   categories and whether it has a DOI."* Claude takes the `arxiv_id` from
   the previous result and calls `get_paper_detail` to answer.

## Project layout

```
week3/
  server/
    main.py          # FastMCP server: tool definitions, stdio entrypoint
    arxiv_client.py  # rate-limited async client + Atom XML parsing for arXiv
    README.md
  tests/             # pytest suite (mocked HTTP, no network access)
```
