<script setup>
defineProps({
  todo: { type: Object, required: true },
});

const emit = defineEmits(["toggle", "delete"]);
</script>

<template>
  <li :class="{ completed: todo.completed }">
    <input
      type="checkbox"
      :checked="todo.completed"
      @change="emit('toggle', todo.id, $event.target.checked)"
    />
    <span>{{ todo.title }}</span>
    <button @click="emit('delete', todo.id)">刪除</button>
  </li>
</template>

<style scoped>
li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

li.completed span {
  text-decoration: line-through;
  color: #999;
}

span {
  flex: 1;
}

button {
  border: none;
  background: transparent;
  cursor: pointer;
  color: #e11d48;
  font-size: 1rem;
}
</style>
