const grid = document.getElementById("notesGrid");
const emptyState = document.getElementById("emptyState");
const noteCount = document.getElementById("noteCount");
const searchInput = document.getElementById("searchInput");
const message = document.getElementById("message");
const dialog = document.getElementById("noteDialog");
const form = document.getElementById("noteForm");
const titleInput = document.getElementById("titleInput");
const contentInput = document.getElementById("contentInput");
const charCount = document.getElementById("charCount");
let editingId = null;
let searchTimer = null;

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      detail = typeof body.detail === "string" ? body.detail : detail;
    } catch (_) {}
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function showMessage(text = "", isError = true) {
  message.textContent = text;
  message.style.color = isError ? "#d94d69" : "#239a78";
}

function escapeHTML(value = "") {
  return String(value).replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  }[char]));
}

function prettyDate(value) {
  const date = new Date(value.replace(" ", "T") + (value.includes("Z") ? "" : "Z"));
  if (Number.isNaN(date.getTime())) return "Just now";
  return date.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

function renderNotes(notes) {
  grid.innerHTML = "";
  noteCount.textContent = String(notes.length);
  emptyState.classList.toggle("visible", notes.length === 0);
  grid.style.display = notes.length ? "grid" : "none";

  notes.forEach(note => {
    const card = document.createElement("article");
    card.className = "note-card";
    card.innerHTML = `
      <div class="note-top">
        <span class="note-badge">Personal note</span>
        <div class="note-menu">
          <button class="mini-button" data-action="edit" data-id="${note.id}" aria-label="Edit ${escapeHTML(note.title)}" title="Edit note">✎</button>
          <button class="mini-button" data-action="delete" data-id="${note.id}" aria-label="Delete ${escapeHTML(note.title)}" title="Delete note">⌫</button>
        </div>
      </div>
      <h3>${escapeHTML(note.title)}</h3>
      <div class="note-content">${escapeHTML(note.content || "No additional details.")}</div>
      <div class="note-bottom"><span>Updated ${escapeHTML(prettyDate(note.updated_at))}</span><span>● Saved</span></div>`;
    grid.appendChild(card);
  });
}

async function loadNotes() {
  try {
    const query = searchInput.value.trim();
    const notes = await api(`/api/notes${query ? `?search=${encodeURIComponent(query)}` : ""}`);
    renderNotes(notes);
    showMessage("");
  } catch (error) {
    showMessage(`Couldn't load notes. ${error.message}`);
  }
}

function openCreateDialog() {
  editingId = null;
  form.reset();
  document.getElementById("dialogEyebrow").textContent = "NEW NOTE";
  document.getElementById("dialogTitle").textContent = "Create a note";
  document.getElementById("saveBtn").textContent = "Save note";
  charCount.textContent = "0 characters";
  dialog.showModal();
  titleInput.focus();
}

async function openEditDialog(id) {
  try {
    const note = await api(`/api/notes/${id}`);
    editingId = id;
    titleInput.value = note.title;
    contentInput.value = note.content;
    document.getElementById("dialogEyebrow").textContent = "EDIT NOTE";
    document.getElementById("dialogTitle").textContent = "Update your note";
    document.getElementById("saveBtn").textContent = "Save changes";
    charCount.textContent = `${contentInput.value.length} characters`;
    dialog.showModal();
    titleInput.focus();
  } catch (error) {
    showMessage(error.message);
  }
}

document.getElementById("newNoteBtn").addEventListener("click", openCreateDialog);
document.getElementById("emptyNewNoteBtn").addEventListener("click", openCreateDialog);
document.getElementById("closeDialog").addEventListener("click", () => dialog.close());
document.getElementById("cancelBtn").addEventListener("click", () => dialog.close());
document.getElementById("allNotesNav").addEventListener("click", () => {
  searchInput.value = "";
  loadNotes();
});

contentInput.addEventListener("input", () => {
  charCount.textContent = `${contentInput.value.length} characters`;
});

searchInput.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadNotes, 180);
});

form.addEventListener("submit", async event => {
  event.preventDefault();
  const title = titleInput.value.trim();
  const content = contentInput.value.trim();
  if (!title) {
    showMessage("Please enter a title.");
    titleInput.focus();
    return;
  }
  const saveButton = document.getElementById("saveBtn");
  saveButton.disabled = true;
  saveButton.textContent = "Saving…";
  try {
    await api(editingId ? `/api/notes/${editingId}` : "/api/notes", {
      method: editingId ? "PUT" : "POST",
      body: JSON.stringify({ title, content })
    });
    dialog.close();
    showMessage(editingId ? "Note updated successfully." : "Note saved successfully.", false);
    await loadNotes();
  } catch (error) {
    showMessage(error.message);
  } finally {
    saveButton.disabled = false;
    saveButton.textContent = editingId ? "Save changes" : "Save note";
  }
});

grid.addEventListener("click", async event => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const id = Number(button.dataset.id);
  if (button.dataset.action === "edit") {
    await openEditDialog(id);
  } else if (button.dataset.action === "delete") {
    const card = button.closest(".note-card");
    const title = card?.querySelector("h3")?.textContent || "this note";
    if (!window.confirm(`Delete "${title}"? This cannot be undone.`)) return;
    try {
      await api(`/api/notes/${id}`, { method: "DELETE" });
      showMessage("Note deleted.", false);
      await loadNotes();
    } catch (error) {
      showMessage(error.message);
    }
  }
});

document.addEventListener("keydown", event => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    searchInput.focus();
  }
});

loadNotes();
