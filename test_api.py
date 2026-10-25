import os
import tempfile
from pathlib import Path

# Keep test data separate from the user's application database.
TEST_DB = Path(tempfile.gettempdir()) / "codenova_notes_test.db"
os.environ["CODENOVA_TEST_DB"] = str(TEST_DB)

from fastapi.testclient import TestClient
import main


def setup_module():
    if TEST_DB.exists():
        TEST_DB.unlink()
    main.DB_PATH = TEST_DB
    main.initialize_database()


def teardown_module():
    if TEST_DB.exists():
        TEST_DB.unlink()


client = TestClient(main.app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_list_update_delete_note():
    created = client.post("/api/notes", json={"title": "Study plan", "content": "Finish project"})
    assert created.status_code == 201
    note = created.json()
    note_id = note["id"]
    assert note["title"] == "Study plan"

    listed = client.get("/api/notes")
    assert listed.status_code == 200
    assert any(item["id"] == note_id for item in listed.json())

    updated = client.put(f"/api/notes/{note_id}", json={"title": "Updated study plan"})
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated study plan"
    assert updated.json()["content"] == "Finish project"

    deleted = client.delete(f"/api/notes/{note_id}")
    assert deleted.status_code == 204
    missing = client.get(f"/api/notes/{note_id}")
    assert missing.status_code == 404


def test_search_notes():
    client.post("/api/notes", json={"title": "Python revision", "content": "Practice FastAPI"})
    response = client.get("/api/notes", params={"search": "FastAPI"})
    assert response.status_code == 200
    assert any("Python revision" == note["title"] for note in response.json())


def test_empty_title_rejected():
    response = client.post("/api/notes", json={"title": "   ", "content": "No title"})
    assert response.status_code == 422
