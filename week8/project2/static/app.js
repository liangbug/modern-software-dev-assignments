const listEl = document.getElementById("todo-list");
const formEl = document.getElementById("todo-form");
const titleInput = document.getElementById("todo-title");

async function fetchTodos() {
  const res = await fetch("/api/todos");
  const todos = await res.json();
  render(todos);
}

function render(todos) {
  listEl.innerHTML = "";
  for (const todo of todos) {
    const li = document.createElement("li");
    li.className = todo.completed ? "completed" : "";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = todo.completed;
    checkbox.addEventListener("change", () => toggleTodo(todo.id, checkbox.checked));

    const span = document.createElement("span");
    span.textContent = todo.title;

    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "刪除";
    deleteBtn.addEventListener("click", () => deleteTodo(todo.id));

    li.append(checkbox, span, deleteBtn);
    listEl.appendChild(li);
  }
}

async function createTodo(title) {
  await fetch("/api/todos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  await fetchTodos();
}

async function toggleTodo(id, completed) {
  await fetch(`/api/todos/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ completed }),
  });
  await fetchTodos();
}

async function deleteTodo(id) {
  await fetch(`/api/todos/${id}`, { method: "DELETE" });
  await fetchTodos();
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = titleInput.value.trim();
  if (!title) return;
  await createTodo(title);
  titleInput.value = "";
});

fetchTodos();
