"""Pulse generation errors."""

from __future__ import annotations


class PulseError(Exception):
    """Base error for pulse pipeline."""


class PulseValidationError(PulseError):
    """Pulse failed constraint validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))
