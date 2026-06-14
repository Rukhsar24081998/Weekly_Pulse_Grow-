"""Push pipeline artifacts from GitHub Actions (no Railway volume needed)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.auth import require_sync_secret
from src.api.services.storage import save_sync_bundle

router = APIRouter(tags=["sync"])


@router.post("/sync/artifacts")
def sync_artifacts(
    payload: dict[str, Any],
    _: None = Depends(require_sync_secret),
) -> dict[str, Any]:
    try:
        written = save_sync_bundle(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok", "written": written}
