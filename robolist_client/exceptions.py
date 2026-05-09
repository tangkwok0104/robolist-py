class RobolistError(Exception):
    """Base exception for robolist-client errors."""


class NotFoundError(RobolistError):
    """Raised when a resource is not found (HTTP 404)."""


class RateLimitError(RobolistError):
    """Raised when the server returns HTTP 429."""


class ParseError(RobolistError):
    """Raised when expected JSON-LD structured data is absent from the page."""
