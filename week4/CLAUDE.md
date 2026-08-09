# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Scope

This is `week4/` of a multi-week assignment repo (see repo-root `CLAUDE.md` for cross-week conventions).
Week 4's own goal, per `assignment.md`: build 2+ Claude Code automations (slash commands in
`.claude/commands/*.md`, CLAUDE.md guidance, and/or SubAgents) that meaningfully improve the dev workflow
on top of the starter app below, then use those automations to extend the app and document everything in
`writeup.md`. `.claude/agents/` and `.claude/skills/` are empty as of now — automations are still to be
built, not pre-existing infra.

## Commands (run from inside `week4/`)

```bash
make run     # uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
make test    # pytest -q backend/tests
make format  # black . && ruff check . --fix
make lint    # ruff check .
make seed    # python -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
```

Single test: `pytest -q backend/tests/test_notes.py::test_create_note`. `PYTHONPATH=.` is exported by the
Makefile; set it manually if running pytest/uvicorn outside `make`.

## Architecture

```
backend/app/
  main.py              # FastAPI app: mounts frontend/ as static, creates tables + seeds DB on startup
  db.py                # SQLAlchemy engine/session (SQLite at data/app.db, override via DATABASE_PATH);
                        # apply_seed_if_needed() loads data/seed.sql only on first run
  models.py            # Note, ActionItem SQLAlchemy models
  schemas.py           # Pydantic *Create / *Read pairs
  routers/notes.py      # /notes CRUD + GET /notes/search/?q=
  routers/action_items.py
  services/extract.py   # extract_action_items(text) — heuristic line-based extraction
frontend/               # plain HTML/CSS/JS, no build step, served via FastAPI StaticFiles
data/app.db, data/seed.sql
docs/TASKS.md           # discrete tasks to practice agent-driven workflows against this app
```

Tests use a `client` fixture (`backend/tests/conftest.py`) that overrides `get_db` with a temp-file SQLite
DB, so tests never touch `data/app.db`.

### `docs/TASKS.md` — candidate tasks to drive automations against

Pre-commit setup, `/notes/search` extension, action-item completion flow, tag parsing in `extract.py`,
notes CRUD (edit/delete), request validation/error handling, and a docs-drift check against `/openapi.json`.
Use these as the concrete workflow an automation (slash command / subagent) is exercised on — don't invent
unrelated feature work when demonstrating an automation.

## Deliverables to keep in sync

- Automations live in `.claude/commands/*.md` (slash commands) and/or subagent configs — check these exist
  and are documented before considering the assignment's Part I done.
- `writeup.md` at `week4/` root has a fixed template (Design inspiration / Design / How to run / Before vs.
  after / How it enhanced the app) per automation — fill it in as automations are built and used, don't
  leave it for the end.
