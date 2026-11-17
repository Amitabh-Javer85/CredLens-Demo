# CredLens Demo backend

The backend is a FastAPI and Celery demonstration using fictional applicants, mocked data providers, illustrative assessment calculations, and an optional Claude-generated memo. Start with the [project README](../README.md) for the supported Docker Compose walkthrough and configuration table.

## Local Python workflow

From this directory in Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
$env:ANTHROPIC_API_KEY = ''
$env:CLAUDE_MODEL = ''
.venv\Scripts\python scripts/demo_memo.py --applicant APP-DEMO-001
.venv\Scripts\python -m pytest tests -q
```

The CLI uses canned memo generation when `ANTHROPIC_API_KEY` or `CLAUDE_MODEL` is absent and runs without background services. The API entrypoint is `src.main:app`. Its job endpoints use Redis and a Celery worker, both supplied by the root Compose stack.

Set configuration through process environment variables, using the names in [.env.example](.env.example). The local demo routes accept fixture IDs only and have no authentication.
