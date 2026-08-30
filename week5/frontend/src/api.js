async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) {
    throw new Error(await res.text());
  }
  if (res.status === 204) {
    return null;
  }
  return res.json();
}

export function listNotes() {
  return fetchJSON("/notes/");
}

export function searchNotes(q) {
  const params = q ? `?q=${encodeURIComponent(q)}` : "";
  return fetchJSON(`/notes/search/${params}`);
}

export function getNote(id) {
  return fetchJSON(`/notes/${id}`);
}

export function createNote({ title, content }) {
  return fetchJSON("/notes/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
  });
}

export function updateNote(id, { title, content }) {
  return fetchJSON(`/notes/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title, content }),
  });
}

export function deleteNote(id) {
  return fetchJSON(`/notes/${id}`, { method: "DELETE" });
}

export function listActionItems() {
  return fetchJSON("/action-items/");
}

export function createActionItem({ description }) {
  return fetchJSON("/action-items/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ description }),
  });
}

export function completeActionItem(id) {
  return fetchJSON(`/action-items/${id}/complete`, { method: "PUT" });
}
