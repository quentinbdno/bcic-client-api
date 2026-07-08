"""Public SDK exception types."""


class BCICError(Exception):
    """Base exception for failures exposed by the BCIC SDK."""


class ConfigurationError(BCICError):
    """Raised when BCIC client configuration is missing or invalid."""


class ValidationError(BCICError):
    """Raised when data fails validation at a public SDK model boundary."""
