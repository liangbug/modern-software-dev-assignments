import sqlite3


def row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_todos(db: sqlite3.Connection) -> list[dict]:
    rows = db.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
    return [row_to_dict(row) for row in rows]


def get_todo(db: sqlite3.Connection, todo_id: int) -> dict | None:
    row = db.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
    return row_to_dict(row) if row else None


def create_todo(db: sqlite3.Connection, title: str) -> dict:
    cursor = db.execute("INSERT INTO todos (title, completed) VALUES (?, 0)", (title,))
    db.commit()
    return get_todo(db, cursor.lastrowid)


def update_todo(
    db: sqlite3.Connection, todo_id: int, title: str | None, completed: bool | None
) -> dict | None:
    existing = get_todo(db, todo_id)
    if existing is None:
        return None

    new_title = title if title is not None else existing["title"]
    new_completed = completed if completed is not None else existing["completed"]

    db.execute(
        "UPDATE todos SET title = ?, completed = ?, updated_at = datetime('now') " "WHERE id = ?",
        (new_title, int(new_completed), todo_id),
    )
    db.commit()
    return get_todo(db, todo_id)


def delete_todo(db: sqlite3.Connection, todo_id: int) -> bool:
    cursor = db.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    db.commit()
    return cursor.rowcount > 0
