"""Public SDK exception types."""


class BCICError(Exception):
    """Base exception for failures exposed by the BCIC SDK."""


class ConfigurationError(BCICError):
    """Raised when BCIC client configuration is missing or invalid."""


class ValidationError(BCICError):
    """Raised when data fails validation at a public SDK model boundary."""


class APIError(BCICError):
    """Raised for a generic BCIC API or response failure."""


class AuthenticationError(BCICError):
    """Raised when BCIC authentication or session establishment fails."""


class AuthorizationError(BCICError):
    """Raised when the authenticated user lacks permission."""


class RateLimitError(BCICError):
    """Raised when BCIC rate-limits a request."""


class NotFoundError(BCICError):
    """Raised when a requested BCIC resource does not exist."""


class ServerError(BCICError):
    """Raised for a transient BCIC server failure."""


class NetworkError(APIError):
    """Raised for a sanitized network or timeout failure."""
