"""Shared secret auth for artifact sync."""

from __future__ import annotations

import os
from typing import Optional

from fastapi import Header, HTTPException


def require_sync_secret(authorization: Optional[str] = Header(default=None)) -> None:
    expected = os.environ.get("SYNC_SECRET", "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="SYNC_SECRET is not configured on this API server",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != expected:
        raise HTTPException(status_code=403, detail="Invalid sync token")
