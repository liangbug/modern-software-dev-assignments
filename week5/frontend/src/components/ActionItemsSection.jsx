import { useEffect, useState } from "react";
import {
  bulkCompleteActionItems,
  completeActionItem,
  createActionItem,
  listActionItems,
} from "../api.js";

const FILTERS = {
  all: { label: "全部", completed: undefined },
  completed: { label: "已完成", completed: true },
  open: { label: "未完成", completed: false },
};

export default function ActionItemsSection() {
  const [items, setItems] = useState([]);
  const [description, setDescription] = useState("");
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");
  const [selectedIds, setSelectedIds] = useState([]);

  async function refresh(currentFilter = filter) {
    try {
      const data = await listActionItems({ completed: FILTERS[currentFilter].completed });
      setItems(data);
      setSelectedIds((prev) => prev.filter((id) => data.some((item) => item.id === id)));
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh(filter);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await createActionItem({ description });
      setDescription("");
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleComplete(id) {
    try {
      await completeActionItem(id);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  function toggleSelected(id) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleBulkComplete() {
    try {
      await bulkCompleteActionItems(selectedIds);
      setSelectedIds([]);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section>
      <h2>Action Items</h2>
      {error && <p role="alert">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          aria-label="Action description"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
        <button type="submit">Add</button>
      </form>
      <div role="group" aria-label="Filter action items">
        {Object.entries(FILTERS).map(([key, { label }]) => (
          <button
            key={key}
            type="button"
            aria-pressed={filter === key}
            disabled={filter === key}
            onClick={() => setFilter(key)}
          >
            {label}
          </button>
        ))}
      </div>
      <button
        type="button"
        onClick={handleBulkComplete}
        disabled={selectedIds.length === 0}
      >
        Complete Selected
      </button>
      <ul>
        {items.map((a) => (
          <li key={a.id}>
            <input
              type="checkbox"
              aria-label={`Select ${a.description}`}
              checked={selectedIds.includes(a.id)}
              disabled={a.completed}
              onChange={() => toggleSelected(a.id)}
            />
            {a.description} [{a.completed ? "done" : "open"}]
            {!a.completed && <button onClick={() => handleComplete(a.id)}>Complete</button>}
          </li>
        ))}
      </ul>
    </section>
  );
}
