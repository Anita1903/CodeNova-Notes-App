# Start here — CodeNova Notes Application

This folder contains the Notes Application project.

1. Install Python from https://www.python.org/downloads/windows/ and select **Add python.exe to PATH**.
2. Open Command Prompt in this folder.
3. Run the following commands one at a time:

```bat
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

4. Open http://127.0.0.1:8000
5. Run automated tests in another terminal after installing dependencies: `python -m pytest -q`

Read `README.md` for features, API routes, testing, and submission preparation.
