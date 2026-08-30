# API Reference

## Route Deltas
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

## root
### GET /
Returns the built frontend's `index.html` (`frontend/dist/index.html`).

## notes
### GET /notes/
List all notes.
- Query params: `tag` (string, optional) — filter to notes tagged with this name (case-insensitive)
- Response `200`: array of `NoteRead`

### POST /notes/
Create a note. Any `#hashtag`s found in `content` are auto-created/reused and attached to the note.
- Body: `NoteCreate` — `{ "title": string, "content": string }`
- Response `201`: `NoteRead`
- Response `422`: validation error

### GET /notes/search/
Search notes by title/content, case-insensitive substring match, with pagination, sorting, and tag filtering.
- Query params:
  - `q` (string, optional) — keyword matched case-insensitively against `title`/`content`
  - `tag` (string, optional) — filter to notes tagged with this name (case-insensitive)
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
Update a note's title/content. Any `#hashtag`s found in the new `content` are auto-created/reused and attached to the note (existing tags are kept).
- Path params: `note_id` (integer)
- Body: `NoteCreate` — `{ "title": string, "content": string }`
- Response `200`: `NoteRead`
- Response `422`: validation error (404 raised at runtime if not found)

### DELETE /notes/{note_id}
Delete a note.
- Path params: `note_id` (integer)
- Response `204`: no content
- Response `422`: validation error (404 raised at runtime if not found)

### POST /notes/{note_id}/extract
Parse `#hashtag`s and action items out of the note's `content` without modifying it. Action items are recognized from `- [ ] task text` checkbox lines as well as legacy `TODO:`/trailing-`!` markers. When `apply=true`, the parsed tags are attached to the note (via the same get-or-create/dedupe logic as note creation) and each parsed action item is persisted as a new `ActionItem` row; when omitted or `false`, nothing is written to the DB.
- Path params: `note_id` (integer)
- Query params: `apply` (boolean, optional, default `false`)
- Response `200`: `NoteExtractResult`
- Response `404`: note not found

## tags
### GET /tags
List all tags, sorted by name.
- Response `200`: array of `TagRead`

### POST /tags
Create a tag, or return the existing tag if one with the same name (case-insensitive) already exists.
- Body: `TagCreate` — `{ "name": string }`
- Response `201`: `TagRead`
- Response `422`: validation error

### DELETE /tags/{tag_id}
Delete a tag entirely (removes it from any notes it was attached to).
- Path params: `tag_id` (integer)
- Response `204`: no content
- Response `404`: tag not found

### POST /notes/{note_id}/tags
Attach a tag to a note by name, creating the tag if it doesn't already exist. Idempotent — attaching an already-attached tag does not create a duplicate association.
- Path params: `note_id` (integer)
- Body: `TagCreate` — `{ "name": string }`
- Response `201`: `NoteRead` (including updated `tags`)
- Response `404`: note not found
- Response `422`: validation error

### DELETE /notes/{note_id}/tags/{tag_id}
Detach a tag from a note (the tag itself is not deleted).
- Path params: `note_id` (integer), `tag_id` (integer)
- Response `200`: `NoteRead` (including updated `tags`)
- Response `404`: note not found, or tag not attached to note

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

### NoteExtractResult
```json
{ "tags": ["string"], "action_items": ["string"] }
```
