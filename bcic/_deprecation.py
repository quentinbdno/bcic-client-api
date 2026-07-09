"""Internal support for consistent public API deprecation warnings."""

import warnings


def warn_deprecated(name: str, *, replacement: str, removal: str) -> None:
    """Warn that an API is deprecated with replacement and removal guidance."""
    warnings.warn(
        f"{name} is deprecated; use {replacement} instead; removal in {removal}",
        DeprecationWarning,
        stacklevel=2,
    )
