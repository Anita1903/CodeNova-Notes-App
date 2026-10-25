from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "notes.db"
STATIC_DIR = BASE_DIR / "static"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="CodeNova Notes API",
    description="A simple REST API for creating, searching, updating, and deleting notes.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(default="", max_length=10000)

    @classmethod
    def clean_fields(cls, values):
        return values


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    content: Optional[str] = Field(default=None, max_length=10000)


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    content: str
    created_at: str
    updated_at: str


def normalize_title(title: str) -> str:
    title = title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Title cannot be empty.")
    return title


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "CodeNova Notes API"}


@app.get("/api/notes", response_model=list[NoteOut])
def list_notes(search: str = Query(default="", max_length=120)):
    search = search.strip()
    with get_connection() as conn:
        if search:
            pattern = f"%{search}%"
            rows = conn.execute(
                """SELECT * FROM notes
                   WHERE title LIKE ? OR content LIKE ?
                   ORDER BY updated_at DESC, id DESC""",
                (pattern, pattern),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM notes ORDER BY updated_at DESC, id DESC"
            ).fetchall()
    return [dict(row) for row in rows]


@app.post("/api/notes", response_model=NoteOut, status_code=201)
def create_note(note: NoteCreate):
    title = normalize_title(note.title)
    content = note.content.strip()
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content) VALUES (?, ?)",
            (title, content),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return dict(row)


@app.get("/api/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: int):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found.")
    return dict(row)


@app.put("/api/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: int, note: NoteUpdate):
    if note.title is None and note.content is None:
        raise HTTPException(status_code=400, detail="Provide a title or content to update.")
    updates = []
    values = []
    if note.title is not None:
        updates.append("title = ?")
        values.append(normalize_title(note.title))
    if note.content is not None:
        updates.append("content = ?")
        values.append(note.content.strip())
    updates.append("updated_at = CURRENT_TIMESTAMP")
    values.append(note_id)
    with get_connection() as conn:
        cursor = conn.execute(
            f"UPDATE notes SET {', '.join(updates)} WHERE id = ?",
            values,
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Note not found.")
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    return dict(row)


@app.delete("/api/notes/{note_id}", status_code=204)
def delete_note(note_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Note not found.")
    return None
