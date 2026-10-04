import { useEffect, useState } from 'react';
import { Todo } from './types';
import { todoService } from './api/todoService';
import './index.css';

export default function App() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [newTitle, setNewTitle] = useState('');

  const loadTodos = async () => {
    try {
      setLoading(true);
      const data = await todoService.getAll();
      setTodos(data);
    } catch (err) {
      setError('Failed to load todos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadTodos(); }, []);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    try {
      const todo = await todoService.create(newTitle);
      setTodos([...todos, todo]);
      setNewTitle('');
    } catch { setError('Failed to add todo'); }
  };

  const toggleTodo = async (todo: Todo) => {
    try {
      const updated = await todoService.update(todo.id, { completed: !todo.completed });
      setTodos(todos.map(t => t.id === todo.id ? updated : t));
    } catch { setError('Failed to update todo'); }
  };

  const deleteTodo = async (id: number) => {
    try {
      await todoService.delete(id);
      setTodos(todos.filter(t => t.id !== id));
    } catch { setError('Failed to delete todo'); }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-md mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Todo List</h1>
      {error && <p className="text-red-500 mb-4">{error}</p>}

      <form onSubmit={handleAdd} className="flex gap-2 mb-6">
        <input
          className="border p-2 flex-1 rounded"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="New task..."
        />
        <button className="bg-blue-500 text-white px-4 py-2 rounded">Add</button>
      </form>

      {todos.length === 0 ? (
        <p className="text-gray-500">No tasks yet.</p>
      ) : (
        <ul className="space-y-2">
          {todos.map(todo => (
            <li key={todo.id} className="flex items-center gap-2 border p-2 rounded">
              <input type="checkbox" checked={todo.completed} onChange={() => toggleTodo(todo)} />
              <span className={todo.completed ? 'line-through flex-1' : 'flex-1'}>{todo.title}</span>
              <button onClick={() => deleteTodo(todo.id)} className="text-red-500">Delete</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
