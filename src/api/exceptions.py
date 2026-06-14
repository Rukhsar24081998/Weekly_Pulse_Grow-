"""API-specific errors."""


class ArtifactNotFoundError(FileNotFoundError):
    """Raised when a phase artifact is missing on disk."""
