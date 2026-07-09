"""Defensive structured-context sanitization for SDK diagnostics."""

from collections.abc import Mapping, Sequence

REDACTED = "[REDACTED]"
_MAX_DEPTH = 8
_SENSITIVE_KEYS = frozenset(
    {
        "authorization",
        "binary",
        "body",
        "content",
        "cookie",
        "credential",
        "credentials",
        "filedata",
        "password",
        "payload",
        "secret",
        "session",
        "sessionid",
        "token",
        "value",
    }
)


def _sensitive(key: object) -> bool:
    if not isinstance(key, str):
        return False
    normalized = "".join(
        character for character in key.casefold() if character.isalnum()
    )
    return normalized in _SENSITIVE_KEYS or any(
        marker in normalized
        for marker in ("password", "authorization", "sessionid", "token", "secret")
    )


def sanitize_context(value: object) -> object:
    """Return a redacted copy of simple structured diagnostic context."""
    return _sanitize(value, depth=0, active=set())


def _sanitize(value: object, *, depth: int, active: set[int]) -> object:
    if depth >= _MAX_DEPTH:
        return REDACTED
    if isinstance(value, bytes | bytearray | memoryview):
        return REDACTED
    if value is None or isinstance(value, str | int | float | bool):
        return value
    identity = id(value)
    if identity in active:
        return REDACTED
    if isinstance(value, Mapping):
        active.add(identity)
        mapping_result = {
            key: (
                REDACTED
                if _sensitive(key)
                else _sanitize(item, depth=depth + 1, active=active)
            )
            for key, item in value.items()
        }
        active.remove(identity)
        return mapping_result
    if isinstance(value, Sequence):
        active.add(identity)
        sequence_result = [
            _sanitize(item, depth=depth + 1, active=active) for item in value
        ]
        active.remove(identity)
        return sequence_result
    return REDACTED
