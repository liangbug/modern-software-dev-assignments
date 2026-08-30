import { useEffect, useState } from "react";
import { createNote, deleteNote, listNotes, updateNote } from "../api.js";

export default function NotesSection() {
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");

  async function refresh() {
    try {
      const data = await listNotes();
      setNotes(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await createNote({ title, content });
      setTitle("");
      setContent("");
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteNote(id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  function startEdit(note) {
    setEditingId(note.id);
    setEditTitle(note.title);
    setEditContent(note.content);
  }

  function cancelEdit() {
    setEditingId(null);
  }

  async function handleUpdate(id) {
    try {
      await updateNote(id, { title: editTitle, content: editContent });
      setEditingId(null);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section>
      <h2>Notes</h2>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          aria-label="Note title"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <input
          aria-label="Note content"
          placeholder="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
        <button type="submit">Add</button>
      </form>
      <ul>
        {notes.map((n) =>
          editingId === n.id ? (
            <li key={n.id}>
              <input
                aria-label={`Edit title ${n.id}`}
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
              />
              <input
                aria-label={`Edit content ${n.id}`}
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
              />
              <button onClick={() => handleUpdate(n.id)}>Save</button>
              <button onClick={cancelEdit}>Cancel</button>
            </li>
          ) : (
            <li key={n.id}>
              {n.title}: {n.content}
              <button onClick={() => startEdit(n)}>Edit</button>
              <button onClick={() => handleDelete(n.id)}>Delete</button>
            </li>
          )
        )}
      </ul>
    </section>
  );
}
