# API Reference

Only the `/notes/` endpoints are documented here (created while adding tag extraction).
`/action_items/` endpoints are not yet documented — out of scope for this update.

## Notes (`/notes/`)

### `GET /notes/`
List all notes.

- Request: none
- Response: `200 OK`, `list[NoteRead]`

### `POST /notes/`
Create a note. `tags` is derived automatically from `content` — any `#word` token is parsed
into a lowercase tag (duplicates collapsed, first-seen order kept) and stored on the note. It is
not accepted as client input.

- Request body (`NoteCreate`):
  ```json
  { "title": "string", "content": "string" }
  ```
- Response: `201 Created`, `NoteRead`
  ```json
  { "id": 1, "title": "string", "content": "string", "tags": ["urgent", "followup"] }
  ```
- Example: `content = "Plan trip #urgent #followup rest of note"` -> `tags = ["urgent", "followup"]`
- Notes with no `#tag` tokens in `content` get `tags = []`.

### `GET /notes/search/`
Search notes by title/content substring (case-sensitive `contains`, matches existing behavior).

- Query params: `q` (optional string)
- Response: `200 OK`, `list[NoteRead]`

### `GET /notes/{note_id}`
Fetch a single note by id.

- Response: `200 OK`, `NoteRead`, or `404 Not Found` if the id does not exist.

## Schemas

### `NoteCreate` (request)
| field   | type   | notes                          |
|---------|--------|---------------------------------|
| title   | string | required                        |
| content | string | required; `#tag` tokens parsed  |

### `NoteRead` (response)
| field   | type       | notes                                              |
|---------|------------|-----------------------------------------------------|
| id      | int        |                                                       |
| title   | string     |                                                       |
| content | string     |                                                       |
| tags    | list[str]  | new — parsed from `content` at creation time, lowercased, de-duplicated, order of first appearance |

Returned by `GET /notes/`, `POST /notes/`, `GET /notes/search/`, and `GET /notes/{note_id}` —
all four now include `tags`.
