# CodeNova Notes Application

A responsive full-stack notes application built with **FastAPI**, **SQLite**, HTML, CSS, and JavaScript.

## Features

- Create, read, update, and delete notes (CRUD).
- Search notes by title or content.
- Persistent SQLite database (`notes.db` is created automatically).
- Responsive layout for desktop and mobile screens.
- Input validation and useful API error responses.
- REST API documented automatically with Swagger UI.
- Automated API tests.

## Tech stack

- Python 3.10+
- FastAPI and Uvicorn
- SQLite
- HTML, CSS, JavaScript
- Pytest and HTTPX for tests

## Run on Windows

1. Install Python 3 from [python.org](https://www.python.org/downloads/windows/). During installation, enable **Add python.exe to PATH**.
2. Extract the project ZIP and open the `CodeNova_Notes_Application` folder.
3. Open Command Prompt in that folder (click File Explorer's address bar, type `cmd`, and press Enter).
4. Create and activate a virtual environment:

   ```bat
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. Install dependencies:

   ```bat
   python -m pip install -r requirements.txt
   ```

6. Start the server:

   ```bat
   python -m uvicorn main:app --reload
   ```

7. Open:
   - App: http://127.0.0.1:8000
   - API documentation: http://127.0.0.1:8000/docs

Keep the terminal window open while using the app. Press `Ctrl+C` in that window to stop the server.

## Run tests

In an activated virtual environment:

```bat
python -m pytest -q
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/notes` | List notes; optional `?search=term` |
| POST | `/api/notes` | Create a note |
| GET | `/api/notes/{id}` | Get one note |
| PUT | `/api/notes/{id}` | Update a note |
| DELETE | `/api/notes/{id}` | Delete a note |

## Project structure

```text
CodeNova_Notes_Application/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
└── tests/
    └── test_api.py
```

## Screenshots for submission

After running the app, take screenshots showing:
1. The main notes page.
2. A saved note.
3. Search results.
4. The API documentation page.

Add them to a `screenshots/` folder in your GitHub repository if your internship instructions request screenshots.

## GitHub submission checklist

- [ ] Create a public GitHub repository.
- [ ] Upload the project files (not `.venv` or generated database files).
- [ ] Keep this README and add your own project description.
- [ ] Test the app and include genuine screenshots.
- [ ] Submit the public repository link through the official CodeNova submission form.

**Note:** This repository template does not submit itself to the internship provider. You must review the result and submit the repository link yourself.
