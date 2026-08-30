# Week 5

Minimal full‑stack starter for experimenting with autonomous coding agents.

- FastAPI backend with SQLite (SQLAlchemy)
- Static frontend (no Node toolchain needed)
- Minimal tests (pytest)
- Pre-commit (black + ruff)
- Tasks to practice agent-driven workflows

## Quickstart

1) Create and activate a virtualenv, then install dependencies

```bash
cd /Users/mihaileric/Documents/code/modern-software-dev-assignments
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
```

2) (Optional) Install pre-commit hooks

```bash
pre-commit install
```

3) Run the app (from `week5/`)

```bash
cd week5 && make run
```

Open `http://localhost:8000` for the frontend and `http://localhost:8000/docs` for the API docs.

## Structure

```
backend/                # FastAPI app
frontend/               # Static UI served by FastAPI
data/                   # SQLite DB + seed
docs/                   # TASKS for agent-driven workflows
```

## Tests

```bash
cd week5 && make test
```

## Formatting/Linting

```bash
cd week5 && make format
cd week5 && make lint
```

## Configuration

Copy `.env.example` to `.env` (in `week5/`) to override defaults like the database path.

## Deploying to Vercel

The app splits into a static Vite/React build and a Python serverless
function, wired together by `vercel.json` at the `week5/` project root.

1) **Import the project** in Vercel with Root Directory set to `week5/`.

2) **Frontend build** — Vercel runs `cd frontend && npm run build` (see
   `vercel.json` `buildCommand`/`installCommand`), outputting to
   `frontend/dist`. Set the build-time env var `VITE_API_BASE_URL`:
   - Same-project API (Option A below): leave it empty — `/api/*` is
     same-origin.
   - External API (Option B below): set it to that API's base URL, e.g.
     `https://week5-api.fly.dev`.

3) **API — Option A (serverless FastAPI on Vercel, default)**:
   - `api/index.py` imports the FastAPI `app` from `backend/app/main.py`; the
     `@vercel/python` runtime (configured in `vercel.json`) serves it.
   - Dependencies for the function come from `requirements.txt`.
   - `vercel.json` rewrites `/api/*` to that function; every other path falls
     through to the static frontend build.
   - No CORS setup needed since frontend and API share an origin.

4) **API — Option B (backend hosted elsewhere, e.g. Fly.io/Render)**:
   - Deploy `backend/` there instead of using `api/index.py`.
   - Set `ALLOWED_ORIGIN` on that deployment to the Vercel frontend's URL —
     `backend/app/main.py` only adds the CORS middleware when this env var is
     set, so same-origin (Option A) deployments stay untouched.
   - Point the Vercel frontend's `VITE_API_BASE_URL` at that API's URL and
     rebuild.

5) **Rollback**: use Vercel's "Instant Rollback" to the previous deployment
   from the project's Deployments tab — no separate rollback command is
   needed since each deploy is immutable.
