import { Todo } from '../types';

// 使用相對路徑，透過 Vite Proxy 轉發
const API_PREFIX = '/api';

export const todoService = {
  getAll: async (): Promise<Todo[]> => {
    const res = await fetch(`${API_PREFIX}/todos`);
    if (!res.ok) throw new Error('Failed to fetch todos');
    return res.json();
  },

  create: async (title: string): Promise<Todo> => {
    const res = await fetch(`${API_PREFIX}/todos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, completed: false }),
    });
    if (!res.ok) throw new Error('Failed to create todo');
    return res.json();
  },

  update: async (id: number, todo: Partial<Todo>): Promise<Todo> => {
    const res = await fetch(`${API_PREFIX}/todos/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(todo),
    });
    if (!res.ok) throw new Error('Failed to update todo');
    return res.json();
  },

  delete: async (id: number): Promise<void> => {
    const res = await fetch(`${API_PREFIX}/todos/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Failed to delete todo');
  }
};
