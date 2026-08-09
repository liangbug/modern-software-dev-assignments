# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo purpose

Weekly assignments for CS146S ("The Modern Software Developer", Stanford). Each `weekN/` directory is an
**independent, self-contained assignment** — do not assume shared code or config between weeks unless a
file explicitly imports across directories (it won't; each week duplicates the starter app instead of
sharing it). When working on a task, scope your attention to the single `weekN/` directory named in the
task.

## Environment / setup

- Python 3.12, managed with `uv` (there's also a legacy `pyproject-poetry.toml`/`poetry.lock` for Poetry,
  but `uv.lock` + `pyproject.toml` at the repo root are the primary ones).
- Install deps: `uv sync` (or `poetry install --no-interaction` if using Poetry).
- Secrets (Gemini API key, etc.) go in a `.env` file at the repo root — never commit it.
- Root `pyproject.toml` configures `black` (line-length 100) and `ruff` (`select = ["E","F","I","UP","B"]`,
  `ignore = ["E501","B008"]`) for the whole repo. `.pre-commit-config.yaml` runs black, ruff --fix,
  end-of-file-fixer, trailing-whitespace.

## Commands

Weeks 4–7 each have their own `Makefile` (run from inside that `weekN/` directory) with identical targets:

```bash
make run     # uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
make test    # pytest -q backend/tests
make format  # black . && ruff check . --fix
make lint    # ruff check .
make seed    # python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
```

`PYTHONPATH` is exported to `.` by the Makefile, so `backend.app.*` imports resolve — if running commands
manually (not via `make`), set `PYTHONPATH=.` from inside the `weekN/` dir first.

To run a single test: `pytest -q backend/tests/test_notes.py::test_create_note` (from inside `weekN/`).

Week 1 exercises are standalone scripts (`python week1/k_shot_prompting.py`, etc.), no server/tests.
Week 3 is an MCP server: `python week3/server/main.py` (STDIO transport); tests via `pytest week3/tests`.
Week 2 is the original FastAPI+SQLite app but predates the Makefile convention — run it directly with
`uvicorn app.main:app --reload` from inside `week2/`.

## Architecture of the recurring starter app (weeks 2, 4–7)

Each of these weeks reimplements the same minimal app — a notes app that extracts "action items" from free
text — with small per-week variations (that's the point of the assignments: agent-driven refactors, security
fixes, code review practice, etc. layered onto the same base). The shape is consistent:

```
backend/app/
  main.py              # FastAPI app: mounts frontend/ as static, creates tables + seeds DB on startup,
                        # includes routers
  db.py                # SQLAlchemy engine/session (SQLite at data/app.db, path overridable via
                        # DATABASE_PATH env var); apply_seed_if_needed() loads data/seed.sql on first run
  models.py            # SQLAlchemy declarative models: Note, ActionItem
  schemas.py           # Pydantic request/response models (*Create / *Read pairs)
  routers/
    notes.py           # /notes endpoints (CRUD + /notes/search/)
    action_items.py    # /action_items endpoints
  services/
    extract.py         # extract_action_items(text): pulls action items out of note text
                        # (heuristic line-based extraction in most weeks — check week1/ for the
                        # LLM-prompting techniques this could be swapped to use)
frontend/               # plain HTML/CSS/JS, no build step, served by FastAPI's StaticFiles
data/
  app.db                # SQLite file, created on first run
  seed.sql              # seed data applied only when app.db doesn't exist yet
```

Tests (`backend/tests/`) use a `client` fixture (see `conftest.py`) that swaps in a temp-file SQLite DB via
FastAPI's dependency override on `get_db`, so tests never touch `data/app.db`.

When comparing behavior across weeks, `diff -rq weekX/backend weekY/backend` is the fastest way to see what
changed — the per-week deltas are usually small and concentrated in one or two files (e.g. `services/extract.py`,
`routers/notes.py`).

### Per-week deltas worth knowing
- **week4**: adds `.claude/agents/` (code-agent, db-agent, doc-agent, refactor-agent, test-agent) and
  `.claude/skills/` (refactor-module, run-test, sync-docs) — these are the assignment's own deliverables
  (custom Claude Code automations), not infrastructure to preserve/ignore.
- **week5**: same starter app, used as a playground for Warp agentic workflows (no repo-specific tooling
  differences beyond the app itself).
- **week6**: target for a Semgrep security scan/remediation exercise — expect intentionally introduced
  vulnerabilities in `backend/` and `frontend/`, plus a `requirements.txt` (in addition to `uv`/`pyproject`)
  since Semgrep scans dependency manifests directly.
- **week7**: has `docs/TASKS.md` defining discrete implementation tasks meant to be done one-per-branch with
  1-shot AI prompts, each reviewed and opened as its own PR.
- **week8**: no starter code — it's a from-scratch, build-your-own-stack assignment (see `week8/assignment.md`).

## Notes for other weeks

- **week1**: prompting-technique exercises (k-shot, chain-of-thought, self-consistency, reflexion, RAG, tool
  calling) calling Gemini via `week1/gemini_client.py`, which mimics the old `ollama.chat()` interface.
  Requires `GEMINI_API_KEY` in root `.env`.
- **week3**: a custom MCP server wrapping the arXiv API (`week3/server/arxiv_client.py`), exposing tools over
  STDIO transport by default.
