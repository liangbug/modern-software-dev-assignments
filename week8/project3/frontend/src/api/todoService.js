const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok && res.status !== 204) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `request failed: ${res.status}`);
  }
  return res.status === 204 ? null : res.json();
}

export function listTodos() {
  return request("/api/todos");
}

export function createTodo(title) {
  return request("/api/todos", {
    method: "POST",
    body: JSON.stringify({ title }),
  });
}

export function updateTodo(id, changes) {
  return request(`/api/todos/${id}`, {
    method: "PUT",
    body: JSON.stringify(changes),
  });
}

export function deleteTodo(id) {
  return request(`/api/todos/${id}`, { method: "DELETE" });
}
