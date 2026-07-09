import logging

import httpx
import pytest

from bcic import Client
from bcic.exceptions import AuthorizationError
from bcic.utils.logging import REDACTED, sanitize_context


def test_sanitizer_redacts_nested_sensitive_values_without_mutation() -> None:
    original = {
        "method_name": "setBinaryData",
        "password": "password-marker",
        "nested": [
            {"sessionId": "session-marker", "Authorization": "token-marker"},
            b"binary-marker",
        ],
    }
    sanitized = sanitize_context(original)
    assert sanitized == {
        "method_name": "setBinaryData",
        "password": REDACTED,
        "nested": [
            {"sessionId": REDACTED, "Authorization": REDACTED},
            REDACTED,
        ],
    }
    assert original["password"] == "password-marker"


def test_sanitizer_handles_cycles_and_unknown_objects() -> None:
    cyclic: list[object] = []
    cyclic.append(cyclic)
    assert sanitize_context(cyclic) == [REDACTED]
    assert sanitize_context(object()) == REDACTED


def test_transport_and_auth_logs_keep_context_but_exclude_secrets(
    caplog: pytest.LogCaptureFixture,
) -> None:
    binary_marker = "cHJpdmF0ZS1iaW5hcnk="

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/login"):
            return httpx.Response(
                200, json={"status": "ok", "sessionId": "session-marker"}
            )
        return httpx.Response(403, text=binary_marker)

    client = Client(
        base_url="https://example.test",
        username="username-marker",
        password="password-marker",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    caplog.set_level(logging.DEBUG)
    with pytest.raises(AuthorizationError) as error:
        client.binary.set(
            "Object",
            "1",
            "file",
            b"private-binary",
            file_name="private.bin",
            content_type="application/octet-stream",
        )
    logs = caplog.text
    for marker in (
        "username-marker",
        "password-marker",
        "session-marker",
        "private-binary",
        binary_marker,
        "private.bin",
    ):
        assert marker not in logs
        assert marker not in str(error.value)
    assert "setBinaryData" in logs
    assert "status_code=403" in logs


def test_library_does_not_override_consumer_log_level() -> None:
    logger = logging.getLogger("bcic.transport")
    previous = logger.level
    try:
        logger.level = logging.CRITICAL
        Client(
            base_url="https://example.test",
            username="user",
            password="password",
        )
        assert logger.level == logging.CRITICAL
    finally:
        logger.level = previous
