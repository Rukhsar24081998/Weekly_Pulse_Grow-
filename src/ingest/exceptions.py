"""Ingestion errors."""


class IngestionError(Exception):
    """Raised when ingestion cannot proceed."""


class EmptyExportError(IngestionError):
    """Raised when a source export has no usable rows."""
