# Tasks Done

Completion log for items in `docs/TASKS.md` (read-only — this file records status instead of
editing that one). Verified with `make test`: 29 passed.

## #1 — Enable pre-commit and fix the repo
`.pre-commit-config.yaml` exists at the monorepo root (applies to all weeks, incl. `week4/`):
black, `ruff --fix`, `end-of-file-fixer`, `trailing-whitespace`. Hooks are installed
(`.git/hooks/pre-commit` present, pre-commit-generated). Current tree is clean under both
`ruff check .` (`All checks passed!`) and the existing formatting — no outstanding
formatting/lint issues in `week4/`. Note: this config lives at the repo root, not inside
`week4/`, since it is shared across weeks (see root `CLAUDE.md`).

## #4 — Improve extraction logic
Added `extract_tags(text: str) -> list[str]` in `backend/app/services/extract.py` (regex-based
`#tag` parsing, lowercase-normalized, de-duplicated by first-occurrence order, returns `[]` when
no valid tag). `Note` model got a new `tags` column (`sqlalchemy.JSON`, `nullable=False`,
`default=list`, `server_default="[]"`); `NoteRead` schema got `tags: list[str] = []`. `create_note`
calls `extract_tags(payload.content)` and stores the result on the new `Note`. `data/seed.sql`
synced with the new column. Compatibility note: `Base.metadata.create_all` won't `ALTER TABLE` an
existing `data/app.db` — chosen strategy was to document manual rebuild (`rm data/app.db && make
seed`) rather than an automatic migration guard. Tests added in `backend/tests/test_extract.py`
(unit tests for `extract_tags`: multiple tags, duplicate tags, mixed case, no tags, bare `#`) and
`backend/tests/test_notes.py` (integration: `POST /notes/` with `#tag` content returns matching
`tags` in the response). See `docs/plans/note-tags/` for the design/tasks/testing docs. The
optional `POST /notes/{id}/extract` action-item extraction endpoint was explicitly out of scope
for this task.

## #2 — Add search endpoint for notes
`GET /notes/search/?q=` rewritten to be explicitly case-insensitive using SQLAlchemy `ilike`
(`Note.title.ilike(f"%{q}%") | Note.content.ilike(f"%{q}%")`) instead of plain `contains`.
`frontend/app.js`/`index.html` got a search input wired to the endpoint (`searchNotes()`,
following the existing `fetchJSON`/`loadNotes` naming convention). Added a mixed-case query test
in `backend/tests/test_notes.py` (create with one case, search with a different case). See
`docs/plans/notes-search/` for the design/tasks/testing docs. Doc'd in `docs/API.md`.

## #3 — Complete action item flow
No code changes — current behavior already matched the desired contract. Added test coverage in
`backend/tests/test_action_items.py`:
- `PUT /action-items/{id}/complete` on a missing id returns `404` with
  `{"detail": "Action item not found"}`
- Calling it again on an already-completed item is idempotent: still `200`, `completed: true`
  (no error)
Option B (making a repeat complete-call return `409`) was scoped but left unexecuted pending
user confirmation — see `docs/plans/action-item-complete-tests/tasks.md`. Current idempotent
behavior is documented in `docs/API.md`.

## #5 — Notes CRUD enhancements
Added `PUT /notes/{note_id}` (partial update — only non-null fields in the request are applied;
updating `content` re-runs `extract_tags` and replaces `tags`) and `DELETE /notes/{note_id}`
(`204 No Content`, no cascade since `action_items` have no FK to notes). Both return `404`
(`{"detail": "Note not found"}`) for a missing id. `frontend/app.js`/`index.html` got edit/delete
UI wired to these endpoints. Tests added in `backend/tests/test_notes.py`: PUT success, PUT
partial update, PUT missing id (404), DELETE success, DELETE missing id (404), DELETE leaves
`action_items` unaffected. Doc'd in `docs/API.md`.

## #6 — Request validation and error handling
Added `field_validator`-based blank-string rejection (empty string and whitespace-only) on
`NoteCreate.title`, `NoteCreate.content`, `NoteUpdate.title`, `NoteUpdate.content` (optional —
`None` still allowed, meaning "don't change"), and `ActionItemCreate.description`. Violations
return FastAPI's default `422` — no custom exception handler was added, so `backend/app/main.py`
is unchanged. Tests added: `POST /notes/` and `PUT /notes/{id}` with blank/whitespace `title`/
`content` → 422; `POST /action-items/` with blank/whitespace `description` → 422; `GET
/notes/{missing-id}` → 404 (pre-existing behavior, now covered); `PUT /action-items/
{missing-id}/complete` → 404 (pre-existing behavior, now covered). 404 coverage for `PUT`/`DELETE
/notes/{id}` was already added under task #5 and intentionally not duplicated. Doc'd in
`docs/API.md`.

## #7 — Docs drift check (manual for now)
`docs/API.md` exists and was verified against `backend/app/routers/notes.py`,
`backend/app/routers/action_items.py`, and `backend/app/schemas.py`: every endpoint, request/
response field, status code, and validation rule documented matches the current code (no drift
found as of this check). This is still a manual check (task explicitly says "manual for now") —
no automated CI step exists yet; the `.claude/skills/sync-docs/SKILL.md` skill was authored to
help with exactly this kind of check but has no recorded run against this repo yet (see
`writeup.md` Automation #1 discussion).
