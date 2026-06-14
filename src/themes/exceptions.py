"""Theme clustering errors."""


class ThemeError(Exception):
    """Base error for theme pipeline."""


class EmptyCorpusError(ThemeError):
    """No reviews available for clustering."""


class GroqError(ThemeError):
    """Groq API call failed."""
