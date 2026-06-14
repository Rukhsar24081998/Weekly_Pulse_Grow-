"""Health and status routes."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.services.artifacts import artifact_availability, load_pipeline_status
from src.pulse.config_loader import load_pulse_config

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    config = load_pulse_config()
    return {
        "status": "ok",
        "service": "weekly-app-review-pulse-api",
        "product": config.display_name,
        "artifacts": artifact_availability(),
    }


@router.get("/status")
def status() -> dict:
    return load_pipeline_status()
