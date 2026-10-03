<script setup>
import TodoItem from "./TodoItem.vue";

defineProps({
  todos: { type: Array, required: true },
});

const emit = defineEmits(["toggle", "delete"]);
</script>

<template>
  <ul>
    <TodoItem
      v-for="todo in todos"
      :key="todo.id"
      :todo="todo"
      @toggle="(id, completed) => emit('toggle', id, completed)"
      @delete="(id) => emit('delete', id)"
    />
  </ul>
</template>

<style scoped>
ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
</style>
