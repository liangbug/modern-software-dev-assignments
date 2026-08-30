// When frontend and backend are deployed separately (Vercel Option A/B),
// VITE_API_BASE_URL points at the API origin; same-origin deployments (the
// FastAPI app serving this bundle directly) leave it unset and paths stay
// relative.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function fetchJSON(path, options) {
  const url = `${API_BASE_URL}${path}`;
  const res = await fetch(url, options);
  if (!res.ok) {
    throw new Error(await res.text());
  }
  if (res.status === 204) {
    return null;
  }
  return res.json();
}

export function listNotes({ tag = "", page = 1, pageSize = 10 } = {}) {
  const params = new URLSearchParams();
  if (tag) params.set("tag", tag);
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  return fetchJSON(`/notes/?${params.toString()}`);
}

export function searchNotes({ q = "", tag = "", page = 1, pageSize = 10, sort = "created_desc" } = {}) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (tag) params.set("tag", tag);
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  params.set("sort", sort);
  return fetchJSON(`/notes/search/?${params.toString()}`);
}

export function listTags() {
  return fetchJSON("/tags");
}

export function createTag(name) {
  return fetchJSON("/tags", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export function attachTagToNote(noteId, name) {
  return fetchJSON(`/notes/${noteId}/tags`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}

export function detachTagFromNote(noteId, tagId) {
  return fetchJSON(`/notes/${noteId}/tags/${tagId}`, { method: "DELETE" });
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

export function listActionItems({ completed, page = 1, pageSize = 10 } = {}) {
  const params = new URLSearchParams();
  if (typeof completed === "boolean") params.set("completed", String(completed));
  params.set("page", String(page));
  params.set("page_size", String(pageSize));
  return fetchJSON(`/action-items/?${params.toString()}`);
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

export function bulkCompleteActionItems(ids) {
  return fetchJSON("/action-items/bulk-complete", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ids }),
  });
}
