import { useEffect, useState } from "react";
import { completeActionItem, createActionItem, listActionItems } from "../api.js";

export default function ActionItemsSection() {
  const [items, setItems] = useState([]);
  const [description, setDescription] = useState("");
  const [error, setError] = useState(null);

  async function refresh() {
    try {
      const data = await listActionItems();
      setItems(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

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
      <ul>
        {items.map((a) => (
          <li key={a.id}>
            {a.description} [{a.completed ? "done" : "open"}]
            {!a.completed && <button onClick={() => handleComplete(a.id)}>Complete</button>}
          </li>
        ))}
      </ul>
    </section>
  );
}
