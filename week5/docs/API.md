# API Reference

Generated from the running app's `/openapi.json` (FastAPI title: "Modern Software Dev Starter (Week 5)", version `0.1.0`).

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
Search notes by title/content substring match.
- Query params: `q` (string, optional)
- Response `200`: array of `NoteRead`
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
List all action items.
- Response `200`: array of `ActionItemRead`

### POST /action-items/
Create an action item.
- Body: `ActionItemCreate` — `{ "description": string }`
- Response `201`: `ActionItemRead`
- Response `422`: validation error

### PUT /action-items/{item_id}/complete
Mark an action item as completed.
- Path params: `item_id` (integer)
- Response `200`: `ActionItemRead`
- Response `422`: validation error (404 raised at runtime if not found)

## Schemas
### NoteCreate
```json
{ "title": "string", "content": "string" }
```

### NoteRead
```json
{ "id": 0, "title": "string", "content": "string" }
```

### ActionItemCreate
```json
{ "description": "string" }
```

### ActionItemRead
```json
{ "id": 0, "description": "string", "completed": false }
```
