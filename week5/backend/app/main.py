import http
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from .db import apply_seed_if_needed, engine
from .models import Base
from .routers import action_items as action_items_router
from .routers import notes as notes_router
from .routers import tags as tags_router

app = FastAPI(title="Modern Software Dev Starter (Week 5)")


def _status_code_to_error_code(status_code: int) -> str:
    try:
        return http.HTTPStatus(status_code).phrase.upper().replace(" ", "_")
    except ValueError:
        return "ERROR"


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": {
                "code": _status_code_to_error_code(exc.status_code),
                "message": str(exc.detail),
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc.errors()),
            },
        },
    )


class ResponseEnvelopeMiddleware(BaseHTTPMiddleware):
    """Wraps successful JSON responses as {"ok": true, "data": <original>}."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        content_type = response.headers.get("content-type", "")
        if response.status_code >= 400 or not content_type.startswith("application/json"):
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        if not body:
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        data = json.loads(body)
        wrapped_body = json.dumps({"ok": True, "data": data}).encode("utf-8")

        headers = dict(response.headers)
        headers["content-length"] = str(len(wrapped_body))

        return Response(
            content=wrapped_body,
            status_code=response.status_code,
            headers=headers,
            media_type="application/json",
        )


app.add_middleware(ResponseEnvelopeMiddleware)

# Allow the deployed Vercel frontend (or any other origin) to call this API
# cross-origin when frontend/backend are deployed separately (see Option B in
# README.md). Same-origin deployment (frontend served by this same app) needs
# no CORS at all, so this stays a no-op unless ALLOWED_ORIGIN is set.
_allowed_origin = os.getenv("ALLOWED_ORIGIN")
if _allowed_origin:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[_allowed_origin],
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Ensure data dir exists
Path("data").mkdir(parents=True, exist_ok=True)

FRONTEND_DIST = Path("frontend/dist")

# Mount built frontend assets (Vite build output)
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    apply_seed_if_needed()


@app.get("/")
async def root() -> FileResponse:
    return FileResponse(str(FRONTEND_DIST / "index.html"))


# Routers
app.include_router(notes_router.router)
app.include_router(action_items_router.router)
app.include_router(tags_router.router)
