# API Reference

Base URL: `http://127.0.0.1:8000` (via `make run`). All request/response bodies are JSON.
Validation errors use FastAPI's default `422 Unprocessable Entity` shape (no custom exception
handler is installed).

## Notes — `/notes`

### `GET /notes/`
List all notes.
- Response `200`: `NoteRead[]`

### `POST /notes/`
Create a note. `tags` is derived automatically from `content` via `extract_tags` (parses `#tag`
tokens) — it is never accepted as request input.
- Request body (`NoteCreate`):
  - `title: str` — required, must not be empty or whitespace-only (422 if blank)
  - `content: str` — required, must not be empty or whitespace-only (422 if blank)
- Response `201`: `NoteRead`

### `GET /notes/search/?q=...`
Search notes by title or content substring, **case-insensitive** (implemented with SQL `ILIKE`,
not plain `contains`). If `q` is omitted or empty, returns all notes (same as `GET /notes/`).
- Query param: `q: str | None`
- Response `200`: `NoteRead[]`
- Example: a note created with title `"Weekly Standup"` is matched by `q=standup`, `q=STANDUP`,
  or `q=Standup` — matching is not tied to the case used at creation time.

### `GET /notes/{note_id}`
Fetch a single note.
- Response `200`: `NoteRead`
- Response `404`: `{"detail": "Note not found"}` if `note_id` does not exist

### `PUT /notes/{note_id}`
Partially update a note. Only fields present (non-`null`) in the request body are changed;
omitted/`null` fields keep their current value. If `content` is updated, `tags` is
re-extracted from the new content via `extract_tags` (old tags are discarded, not merged).
- Request body (`NoteUpdate`):
  - `title: str | None` — if provided, must not be empty/whitespace-only (422 if blank)
  - `content: str | None` — if provided, must not be empty/whitespace-only (422 if blank)
- Response `200`: `NoteRead` (updated note)
- Response `404`: `{"detail": "Note not found"}` if `note_id` does not exist

### `DELETE /notes/{note_id}`
Delete a note. No cascading behavior — `action_items` have no FK/relationship to notes in the
current schema, so they are unaffected by note deletion.
- Response `204`: no body
- Response `404`: `{"detail": "Note not found"}` if `note_id` does not exist

### `NoteRead` shape
```json
{
  "id": 1,
  "title": "string",
  "content": "string",
  "tags": ["string", "..."]
}
```

## Action Items — `/action-items`

### `GET /action-items/`
List all action items.
- Response `200`: `ActionItemRead[]`

### `POST /action-items/`
Create an action item (always starts `completed: false`).
- Request body (`ActionItemCreate`):
  - `description: str` — required, must not be empty or whitespace-only (422 if blank)
- Response `201`: `ActionItemRead`

### `PUT /action-items/{item_id}/complete`
Mark an action item as completed.
- Response `200`: `ActionItemRead` (with `completed: true`)
- Response `404`: `{"detail": "Action item not found"}` if `item_id` does not exist
- **Idempotent**: calling this again on an item that is already `completed: true` still returns
  `200` with `completed: true` (no error, no 409) — this is current, tested behavior, not a bug.

### `ActionItemRead` shape
```json
{
  "id": 1,
  "description": "string",
  "completed": false
}
```

## Validation rules summary

All of the following raise `422` (FastAPI default validation error format) when violated:
- `NoteCreate.title`, `NoteCreate.content` — required, non-blank (rejects `""` and whitespace-only
  strings like `"   "`)
- `NoteUpdate.title`, `NoteUpdate.content` — optional; when provided, non-blank (same rule as
  above); `null`/omitted is allowed and means "don't change this field"
- `ActionItemCreate.description` — required, non-blank

No custom `400` error handling was added; blank-string protection uses Pydantic
`field_validator`s in `backend/app/schemas.py`, and missing-resource lookups use FastAPI's
`HTTPException(status_code=404, ...)` directly in the routers.
