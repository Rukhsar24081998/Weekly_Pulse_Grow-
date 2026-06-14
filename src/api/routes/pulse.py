"""Pulse and themes read routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.services.artifacts import load_latest_pulse, load_latest_themes

router = APIRouter(tags=["pulse"])


@router.get("/pulse/latest")
def pulse_latest() -> dict:
    try:
        return load_latest_pulse()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/themes/latest")
def themes_latest() -> dict:
    try:
        return load_latest_themes()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
