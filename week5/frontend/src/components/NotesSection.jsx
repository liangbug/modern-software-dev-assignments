import { useEffect, useState } from "react";
import { createNote, deleteNote, searchNotes, updateNote } from "../api.js";

const PAGE_SIZE = 10;

export default function NotesSection() {
  const [notes, setNotes] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [query, setQuery] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [error, setError] = useState(null);
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");

  async function refresh(targetPage, targetQuery) {
    try {
      const data = await searchNotes({
        q: targetQuery,
        page: targetPage,
        pageSize: PAGE_SIZE,
      });
      setNotes(data.items);
      setTotal(data.total);
      setPage(data.page);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh(1, "");
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSearchSubmit(e) {
    e.preventDefault();
    await refresh(1, query);
  }

  async function handlePrev() {
    if (page > 1) {
      await refresh(page - 1, query);
    }
  }

  async function handleNext() {
    if (page * PAGE_SIZE < total) {
      await refresh(page + 1, query);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await createNote({ title, content });
      setTitle("");
      setContent("");
      await refresh(1, query);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    const previousNotes = notes;
    const previousTotal = total;
    setError(null);
    setNotes((current) => current.filter((n) => n.id !== id));
    setTotal((current) => Math.max(0, current - 1));
    try {
      await deleteNote(id);
      await refresh(page, query);
    } catch (err) {
      setNotes(previousNotes);
      setTotal(previousTotal);
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
    const previousNotes = notes;
    const nextTitle = editTitle;
    const nextContent = editContent;
    setError(null);
    setNotes((current) =>
      current.map((n) =>
        n.id === id ? { ...n, title: nextTitle, content: nextContent } : n
      )
    );
    setEditingId(null);
    try {
      await updateNote(id, { title: nextTitle, content: nextContent });
      await refresh(page, query);
    } catch (err) {
      setNotes(previousNotes);
      setError(err.message);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <section>
      <h2>Notes</h2>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSearchSubmit}>
        <input
          aria-label="Search notes"
          placeholder="Search notes"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>
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
      <p>
        共 {total} 筆結果，第 {page} / {totalPages} 頁
      </p>
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
      <div>
        <button onClick={handlePrev} disabled={page <= 1}>
          上一頁
        </button>
        <button onClick={handleNext} disabled={page * PAGE_SIZE >= total}>
          下一頁
        </button>
      </div>
    </section>
  );
}
