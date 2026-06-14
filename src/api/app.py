"""FastAPI application factory."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes.health import router as health_router
from src.api.routes.pulse import router as pulse_router

_DEFAULT_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def _cors_origins() -> list[str]:
    extra = os.environ.get("CORS_ORIGINS", "")
    origins = list(_DEFAULT_ORIGINS)
    for item in extra.split(","):
        value = item.strip()
        if value and value not in origins:
            origins.append(value)
    return origins


def create_app() -> FastAPI:
    app = FastAPI(
        title="Weekly App Review Pulse API",
        description="Read-only API over existing pipeline artifacts for frontend use.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    app.include_router(health_router, prefix="/api")
    app.include_router(pulse_router, prefix="/api")

    @app.get("/")
    def root() -> dict[str, str]:
        return {"service": "weekly-app-review-pulse-api", "docs": "/docs"}

    return app


app = create_app()
