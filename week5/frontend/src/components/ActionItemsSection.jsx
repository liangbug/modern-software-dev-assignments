import { useEffect, useState } from "react";
import {
  bulkCompleteActionItems,
  completeActionItem,
  createActionItem,
  listActionItems,
} from "../api.js";

const PAGE_SIZE = 10;

const FILTERS = {
  all: { label: "全部", completed: undefined },
  completed: { label: "已完成", completed: true },
  open: { label: "未完成", completed: false },
};

export default function ActionItemsSection() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [description, setDescription] = useState("");
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState("all");
  const [selectedIds, setSelectedIds] = useState([]);

  async function refresh(currentFilter = filter, targetPage = page) {
    try {
      const data = await listActionItems({
        completed: FILTERS[currentFilter].completed,
        page: targetPage,
        pageSize: PAGE_SIZE,
      });
      setItems(data.items);
      setTotal(data.total);
      setPage(targetPage);
      setSelectedIds((prev) => prev.filter((id) => data.items.some((item) => item.id === id)));
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh(filter, 1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filter]);

  async function handleSubmit(e) {
    e.preventDefault();
    try {
      await createActionItem({ description });
      setDescription("");
      await refresh(filter, 1);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleComplete(id) {
    try {
      await completeActionItem(id);
      await refresh(filter, page);
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
      await refresh(filter, page);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handlePrev() {
    if (page > 1) {
      await refresh(filter, page - 1);
    }
  }

  async function handleNext() {
    if (page * PAGE_SIZE < total) {
      await refresh(filter, page + 1);
    }
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

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
      <p>
        共 {total} 筆結果，第 {page} / {totalPages} 頁
      </p>
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
      <div>
        <button onClick={handlePrev} disabled={page <= 1}>
          上一頁
        </button>
        <button onClick={handleNext} disabled={page * PAGE_SIZE >= total}>
          下一頁
        </button>
      </div>
    </section>
  );
}
