"""Publish pipeline errors."""


class PublishError(Exception):
    """Base error for Phase 4–5 publish."""


class PublishValidationError(PublishError):
    """Pulse failed preflight validation — MCP must not be called."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


class DraftError(PublishError):
    """Gmail draft configuration or MCP draft call failed."""


class McpError(PublishError):
    """MCP HTTP server returned an error or was unreachable."""
