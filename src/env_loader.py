"""Load environment variables from project-root `.env` file."""

from __future__ import annotations

from src.paths import ROOT


def load_env() -> None:
    """Load `.env` from repo root if present. No-op when file or package missing."""
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(env_path, override=False)
