<script setup>
import { onMounted, ref } from "vue";

import { createTodo, deleteTodo, listTodos, updateTodo } from "./api/todoService";
import TodoList from "./components/TodoList.vue";

const todos = ref([]);
const newTitle = ref("");
const error = ref("");

async function refresh() {
  try {
    todos.value = await listTodos();
    error.value = "";
  } catch (e) {
    error.value = e.message;
  }
}

async function onSubmit() {
  const title = newTitle.value.trim();
  if (!title) return;
  await createTodo(title);
  newTitle.value = "";
  await refresh();
}

async function onToggle(id, completed) {
  await updateTodo(id, { completed });
  await refresh();
}

async function onDelete(id) {
  await deleteTodo(id);
  await refresh();
}

onMounted(refresh);
</script>

<template>
  <main class="app">
    <h1>Todo List</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <form @submit.prevent="onSubmit">
      <input v-model="newTitle" type="text" placeholder="新增待辦事項..." autocomplete="off" required />
      <button type="submit">新增</button>
    </form>
    <TodoList :todos="todos" @toggle="onToggle" @delete="onDelete" />
  </main>
</template>

<style>
body {
  font-family: system-ui, -apple-system, sans-serif;
  background: #f5f5f7;
  margin: 0;
  padding: 2rem;
}

.app {
  max-width: 480px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

h1 {
  margin-top: 0;
  font-size: 1.5rem;
}

.error {
  color: #e11d48;
}

form {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

form input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}

form button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  background: #2563eb;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
}
</style>
