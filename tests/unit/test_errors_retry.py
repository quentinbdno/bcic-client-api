from collections.abc import Callable

import httpx
import pytest

from bcic.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    BCICError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from bcic.transport import RestTransport


@pytest.mark.parametrize(
    ("status_code", "exception_type"),
    [
        (400, ValidationError),
        (401, AuthenticationError),
        (403, AuthorizationError),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
    ],
)
def test_http_failures_map_to_sdk_exceptions(
    status_code: int, exception_type: type[BCICError]
) -> None:
    transport = RestTransport(
        "https://example.test",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(status_code, text="secret raw response")
            )
        ),
        max_retries=0,
    )

    with pytest.raises(exception_type) as error:
        transport.execute("getRecord")

    assert "secret raw response" not in str(error.value)


@pytest.mark.parametrize(
    ("payload", "exception_type"),
    [
        ({"status": "login", "err": "expired sid"}, AuthenticationError),
        ({"status": "permission", "err": "private"}, AuthorizationError),
        ({"status": "validation", "err": "private"}, ValidationError),
        ({"status": "error", "err": "private"}, APIError),
    ],
)
def test_bcic_error_envelopes_map_without_raw_messages(
    payload: dict[str, str], exception_type: type[BCICError]
) -> None:
    transport = RestTransport(
        "https://example.test",
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=payload)
            )
        ),
        max_retries=0,
    )

    with pytest.raises(exception_type) as error:
        transport.execute("getRecord")

    assert payload["err"] not in str(error.value)


@pytest.mark.parametrize(
    "response_factory",
    [
        lambda attempt: httpx.Response(503, json={"status": "error"}),
        lambda attempt: httpx.Response(429, json={"status": "error"}),
    ],
)
def test_transient_http_failures_retry_to_configured_limit(
    response_factory: Callable[[int], httpx.Response],
) -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return response_factory(attempts)
        return httpx.Response(200, json={"status": "ok"})

    transport = RestTransport(
        "https://example.test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        max_retries=2,
        retry_wait_seconds=0,
    )

    assert transport.execute("getRecord") == {"status": "ok"}
    assert attempts == 3


def test_network_failure_exhaustion_is_mapped_and_retried() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        raise httpx.ConnectError("private host detail", request=request)

    transport = RestTransport(
        "https://example.test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        max_retries=1,
        retry_wait_seconds=0,
    )

    with pytest.raises(APIError) as error:
        transport.execute("getRecord")

    assert attempts == 2
    assert "private host detail" not in str(error.value)


def test_non_retryable_failure_is_attempted_once() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(403, text="private")

    transport = RestTransport(
        "https://example.test",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
        max_retries=4,
        retry_wait_seconds=0,
    )

    with pytest.raises(AuthorizationError):
        transport.execute("getRecord")

    assert attempts == 1
