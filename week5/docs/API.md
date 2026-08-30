# API Reference

## Route Deltas
- Changed: `NoteCreate` schema now validates `title` (length 1-200) and `content` (length 1-5000); requests outside these bounds return `422`. Applies to `POST /notes/` and `PUT /notes/{note_id}`.
- Changed: `GET /action-items/` now accepts an optional `completed` (boolean) query param to filter by completion status.
- Added: `POST /action-items/bulk-complete` — marks multiple action items completed in a single transaction; rolls back entirely (no partial completion) if any id does not exist.

Generated from the running app's `/openapi.json` (FastAPI title: "Modern Software Dev Starter (Week 5)", version `0.1.0`).

## Route Deltas
- Changed: `GET /notes/search/` — now supports pagination and sorting.
  - Added query params: `page` (integer, default `1`), `page_size` (integer, default `10`), `sort` (string, default `created_desc`; also accepts `title_asc`).
  - Response shape changed from an array of `NoteRead` to `NoteSearchResult` — `{ items: NoteRead[], total: number, page: number, page_size: number }`.
  - `q` matching is now case-insensitive over `title`/`content`.
- Added: `NoteSearchResult` schema.

## root
### GET /
Returns the built frontend's `index.html` (`frontend/dist/index.html`).

## notes
### GET /notes/
List all notes.
- Response `200`: array of `NoteRead`

### POST /notes/
Create a note.
- Body: `NoteCreate` — `{ "title": string, "content": string }`
- Response `201`: `NoteRead`
- Response `422`: validation error

### GET /notes/search/
Search notes by title/content, case-insensitive substring match, with pagination and sorting.
- Query params:
  - `q` (string, optional) — keyword matched case-insensitively against `title`/`content`
  - `page` (integer, optional, default `1`)
  - `page_size` (integer, optional, default `10`)
  - `sort` (string, optional, default `created_desc`) — `created_desc` or `title_asc`
- Response `200`: `NoteSearchResult`
- Response `422`: validation error

### GET /notes/{note_id}
Get a single note by id.
- Path params: `note_id` (integer)
- Response `200`: `NoteRead`
- Response `422`: validation error (404 raised at runtime if not found)

### PUT /notes/{note_id}
Update a note's title/content.
- Path params: `note_id` (integer)
- Body: `NoteCreate` — `{ "title": string, "content": string }`
- Response `200`: `NoteRead`
- Response `422`: validation error (404 raised at runtime if not found)

### DELETE /notes/{note_id}
Delete a note.
- Path params: `note_id` (integer)
- Response `204`: no content
- Response `422`: validation error (404 raised at runtime if not found)

## action_items
### GET /action-items/
List action items, optionally filtered by completion status.
- Query params: `completed` (boolean, optional) — when provided, only returns items matching that completion state
- Response `200`: array of `ActionItemRead`

### POST /action-items/
Create an action item.
- Body: `ActionItemCreate` — `{ "description": string }`
- Response `201`: `ActionItemRead`
- Response `422`: validation error

### POST /action-items/bulk-complete
Mark multiple action items as completed in a single transaction.
- Body: `BulkCompleteRequest` — `{ "ids": [integer, ...] }`
- Response `200`: array of `ActionItemRead` (all requested items, now completed)
- Response `404`: if any id does not exist, the entire batch is rolled back (no items are marked completed) and an error is returned
- Response `422`: validation error

### PUT /action-items/{item_id}/complete
Mark an action item as completed.
- Path params: `item_id` (integer)
- Response `200`: `ActionItemRead`
- Response `422`: validation error (404 raised at runtime if not found)

## Schemas
### NoteCreate
```json
{ "title": "string (1-200 chars)", "content": "string (1-5000 chars)" }
```

### NoteRead
```json
{ "id": 0, "title": "string", "content": "string" }
```

### NoteSearchResult
```json
{ "items": [{ "id": 0, "title": "string", "content": "string" }], "total": 0, "page": 1, "page_size": 10 }
```

### ActionItemCreate
```json
{ "description": "string" }
```

### ActionItemRead
```json
{ "id": 0, "description": "string", "completed": false }
```

### BulkCompleteRequest
```json
{ "ids": [0] }
```
