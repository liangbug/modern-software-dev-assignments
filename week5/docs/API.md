# API Reference

## Route Deltas
- Changed: all successful JSON responses are now wrapped as `{ "ok": true, "data": <original response body> }`. `204 No Content` responses are unchanged (no body).
- Added: global exception handlers.
  - `HTTPException` (e.g. `404 Not Found`) now returns `{ "ok": false, "error": { "code": "<HTTP_STATUS_PHRASE>", "message": "<detail>" } }` (e.g. `code: "NOT_FOUND"`).
  - `RequestValidationError` (`422`) now returns `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": "<validation errors>" } }`.
- Changed: `ActionItemCreate.description` now requires `minLength: 1, maxLength: 2000` (previously unconstrained), returning `422` for empty descriptions.

Previous deltas (still in effect):
- Added: `POST /notes/{note_id}/extract` — parse `#hashtag`s and action items (`- [ ] task text` checkboxes, plus legacy `TODO:`/`!` markers) out of a note's `content`. Returns the parsed result without writing to the DB unless `apply=true`.
- Added: `NoteExtractResult` schema — `{ tags: string[], action_items: string[] }`.
- Changed: `extract_action_items` now also recognizes `- [ ] task text` checkbox lines (returning the task text), in addition to the existing `TODO:`/trailing-`!` markers.
- Added: `Tag` model and `note_tags` many-to-many association between `Note` and `Tag`.
- Added: `GET /tags`, `POST /tags` (get-or-create by name, case-insensitive), `DELETE /tags/{tag_id}`.
- Added: `POST /notes/{note_id}/tags` — attach a tag to a note (creating it if needed; idempotent, no duplicate association).
- Added: `DELETE /notes/{note_id}/tags/{tag_id}` — detach a tag from a note.
- Changed: `NoteRead` now includes a `tags` field (`TagRead[]`, default `[]`).
- Changed: `GET /notes/` and `GET /notes/search/` now accept an optional `tag` (string) query param to filter notes by tag name (case-insensitive).
- Changed: `POST /notes/` and `PUT /notes/{note_id}` now parse `#hashtag`s out of `content` and auto-create/attach matching tags (deduped case-insensitively; existing tags are reused, not duplicated).

Generated from the running app's `/openapi.json` (FastAPI title: "Modern Software Dev Starter (Week 5)", version `0.1.0`).

## Response Envelope
- Success: `{ "ok": true, "data": <payload> }`, where `<payload>` matches the schemas below (unchanged shape, just wrapped).
- Error: `{ "ok": false, "error": { "code": string, "message": string } }`.
  - `code` for `HTTPException`s is the upper-snake-case HTTP status phrase (e.g. `404` → `NOT_FOUND`).
  - `code` for request validation errors is always `VALIDATION_ERROR`, and `message` is the stringified list of Pydantic validation errors.
- `204 No Content` responses (`DELETE /notes/{note_id}`, `DELETE /tags/{tag_id}`) have no body and are not wrapped.

## root
### GET /
Returns the built frontend's `index.html` (`frontend/dist/index.html`). Not wrapped (not JSON).

## notes
### GET /notes/
List all notes.
- Query params: `tag` (string, optional) — filter to notes tagged with this name (case-insensitive)
- Response `200`: `{ "ok": true, "data": NoteRead[] }`

### POST /notes/
Create a note. Any `#hashtag`s found in `content` are auto-created/reused and attached to the note.
- Body: `NoteCreate` — `{ "title": string, "content": string }`
- Response `201`: `{ "ok": true, "data": NoteRead }`
- Response `422`: `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": string } }`

### GET /notes/search/
Search notes by title/content, case-insensitive substring match, with pagination, sorting, and tag filtering.
- Query params:
  - `q` (string, optional) — keyword matched case-insensitively against `title`/`content`
  - `tag` (string, optional) — filter to notes tagged with this name (case-insensitive)
  - `page` (integer, optional, default `1`)
  - `page_size` (integer, optional, default `10`)
  - `sort` (string, optional, default `created_desc`) — `created_desc` or `title_asc`
- Response `200`: `{ "ok": true, "data": NoteSearchResult }`
- Response `422`: `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": string } }`

### GET /notes/{note_id}
Get a single note by id.
- Path params: `note_id` (integer)
- Response `200`: `{ "ok": true, "data": NoteRead }`
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Note not found" } }`

### PUT /notes/{note_id}
Update a note's title/content. Any `#hashtag`s found in the new `content` are auto-created/reused and attached to the note (existing tags are kept).
- Path params: `note_id` (integer)
- Body: `NoteCreate` — `{ "title": string, "content": string }`
- Response `200`: `{ "ok": true, "data": NoteRead }`
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Note not found" } }`
- Response `422`: `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": string } }`

### DELETE /notes/{note_id}
Delete a note.
- Path params: `note_id` (integer)
- Response `204`: no content
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Note not found" } }`

### POST /notes/{note_id}/extract
Parse `#hashtag`s and action items out of the note's `content` without modifying it. Action items are recognized from `- [ ] task text` checkbox lines as well as legacy `TODO:`/trailing-`!` markers. When `apply=true`, the parsed tags are attached to the note (via the same get-or-create/dedupe logic as note creation) and each parsed action item is persisted as a new `ActionItem` row; when omitted or `false`, nothing is written to the DB.
- Path params: `note_id` (integer)
- Query params: `apply` (boolean, optional, default `false`)
- Response `200`: `{ "ok": true, "data": NoteExtractResult }`
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Note not found" } }`

## tags
### GET /tags
List all tags, sorted by name.
- Response `200`: `{ "ok": true, "data": TagRead[] }`

### POST /tags
Create a tag, or return the existing tag if one with the same name (case-insensitive) already exists.
- Body: `TagCreate` — `{ "name": string }`
- Response `201`: `{ "ok": true, "data": TagRead }`
- Response `422`: `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": string } }`

### DELETE /tags/{tag_id}
Delete a tag entirely (removes it from any notes it was attached to).
- Path params: `tag_id` (integer)
- Response `204`: no content
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Tag not found" } }`

### POST /notes/{note_id}/tags
Attach a tag to a note by name, creating the tag if it doesn't already exist. Idempotent — attaching an already-attached tag does not create a duplicate association.
- Path params: `note_id` (integer)
- Body: `TagCreate` — `{ "name": string }`
- Response `201`: `{ "ok": true, "data": NoteRead }` (including updated `tags`)
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Note not found" } }`
- Response `422`: `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": string } }`

### DELETE /notes/{note_id}/tags/{tag_id}
Detach a tag from a note (the tag itself is not deleted).
- Path params: `note_id` (integer), `tag_id` (integer)
- Response `200`: `{ "ok": true, "data": NoteRead }` (including updated `tags`)
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Note not found, or tag not attached to note" } }`

## action_items
### GET /action-items/
List action items, optionally filtered by completion status.
- Query params: `completed` (boolean, optional) — when provided, only returns items matching that completion state
- Response `200`: `{ "ok": true, "data": ActionItemRead[] }`

### POST /action-items/
Create an action item.
- Body: `ActionItemCreate` — `{ "description": string (1-2000 chars) }`
- Response `201`: `{ "ok": true, "data": ActionItemRead }`
- Response `422`: `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": string } }`

### POST /action-items/bulk-complete
Mark multiple action items as completed in a single transaction.
- Body: `BulkCompleteRequest` — `{ "ids": [integer, ...] }`
- Response `200`: `{ "ok": true, "data": ActionItemRead[] }` (all requested items, now completed)
- Response `404`: if any id does not exist, the entire batch is rolled back (no items are marked completed) and `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Action item(s) not found: [...]" } }` is returned
- Response `422`: `{ "ok": false, "error": { "code": "VALIDATION_ERROR", "message": string } }`

### PUT /action-items/{item_id}/complete
Mark an action item as completed.
- Path params: `item_id` (integer)
- Response `200`: `{ "ok": true, "data": ActionItemRead }`
- Response `404`: `{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Action item not found" } }`

## Schemas
### NoteCreate
```json
{ "title": "string (1-200 chars)", "content": "string (1-5000 chars)" }
```

### NoteRead
```json
{ "id": 0, "title": "string", "content": "string", "tags": [{ "id": 0, "name": "string" }] }
```

### NoteSearchResult
```json
{ "items": [{ "id": 0, "title": "string", "content": "string", "tags": [] }], "total": 0, "page": 1, "page_size": 10 }
```

### TagCreate
```json
{ "name": "string (1-100 chars)" }
```

### TagRead
```json
{ "id": 0, "name": "string" }
```

### ActionItemCreate
```json
{ "description": "string (1-2000 chars)" }
```

### ActionItemRead
```json
{ "id": 0, "description": "string", "completed": false }
```

### BulkCompleteRequest
```json
{ "ids": [0] }
```

### NoteExtractResult
```json
{ "tags": ["string"], "action_items": ["string"] }
```

### Error envelope
```json
{ "ok": false, "error": { "code": "NOT_FOUND", "message": "Note not found" } }
```
