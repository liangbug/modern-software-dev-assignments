"""Vercel Python serverless entrypoint: re-exports the FastAPI app.

Vercel's Python runtime looks for an ASGI/WSGI app object in the module
matching the function's file path (`api/index.py` -> routed at `/api/*`, see
vercel.json). The actual app lives in backend/app/main.py; this module just
imports it so Vercel has something to serve.
"""

from backend.app.main import app  # noqa: F401
