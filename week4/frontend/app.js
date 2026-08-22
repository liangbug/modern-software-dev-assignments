async function fetchJSON(url, options) {
  const res = await fetch(url, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function renderNoteItem(n, list, onChanged) {
  const li = document.createElement('li');
  const span = document.createElement('span');
  span.textContent = `${n.title}: ${n.content}`;
  li.appendChild(span);

  const editBtn = document.createElement('button');
  editBtn.textContent = 'Edit';
  editBtn.onclick = async () => {
    const newTitle = prompt('Title', n.title);
    if (newTitle === null) return;
    const newContent = prompt('Content', n.content);
    if (newContent === null) return;
    await fetchJSON(`/notes/${n.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newTitle, content: newContent }),
    });
    onChanged();
  };
  li.appendChild(editBtn);

  const deleteBtn = document.createElement('button');
  deleteBtn.textContent = 'Delete';
  deleteBtn.onclick = async () => {
    await fetch(`/notes/${n.id}`, { method: 'DELETE' });
    onChanged();
  };
  li.appendChild(deleteBtn);

  list.appendChild(li);
}

async function loadNotes() {
  const list = document.getElementById('notes');
  list.innerHTML = '';
  const notes = await fetchJSON('/notes/');
  for (const n of notes) {
    renderNoteItem(n, list, () => {
      loadNotes();
    });
  }
}

async function searchNotes(q) {
  const list = document.getElementById('search-results');
  list.innerHTML = '';
  const notes = await fetchJSON(`/notes/search/?q=${encodeURIComponent(q)}`);
  for (const n of notes) {
    renderNoteItem(n, list, () => {
      searchNotes(q);
      loadNotes();
    });
  }
}

async function loadActions() {
  const list = document.getElementById('actions');
  list.innerHTML = '';
  const items = await fetchJSON('/action-items/');
  for (const a of items) {
    const li = document.createElement('li');
    li.textContent = `${a.description} [${a.completed ? 'done' : 'open'}]`;
    if (!a.completed) {
      const btn = document.createElement('button');
      btn.textContent = 'Complete';
      btn.onclick = async () => {
        await fetchJSON(`/action-items/${a.id}/complete`, { method: 'PUT' });
        loadActions();
      };
      li.appendChild(btn);
    }
    list.appendChild(li);
  }
}

window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('note-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('note-title').value;
    const content = document.getElementById('note-content').value;
    await fetchJSON('/notes/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, content }),
    });
    e.target.reset();
    loadNotes();
  });

  document.getElementById('action-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('action-desc').value;
    await fetchJSON('/action-items/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    e.target.reset();
    loadActions();
  });

  document.getElementById('search-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const q = document.getElementById('search-query').value;
    searchNotes(q);
  });

  loadNotes();
  loadActions();
});
