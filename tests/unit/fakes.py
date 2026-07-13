"""Typed HTTP fakes shared by the offline unit test suite."""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

import httpx

ResponseFactory = Callable[[httpx.Request], httpx.Response]
ResponseSpec = httpx.Response | ResponseFactory


@dataclass
class RequestRecorder:
    """Record requests in call order while delegating response creation."""

    responder: ResponseFactory
    requests: list[httpx.Request] = field(default_factory=list)

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        return self.responder(request)


class SequenceHandler:
    """Return configured responses in order and reject unexpected requests."""

    def __init__(self, responses: Iterable[ResponseSpec]) -> None:
        self._responses = iter(responses)
        self._request_count = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self._request_count += 1
        try:
            response = next(self._responses)
        except StopIteration as error:
            raise AssertionError(
                f"Unexpected HTTP request #{self._request_count}: "
                f"{request.method} {request.url.path}"
            ) from error
        return response(request) if callable(response) else response


def json_response(
    payload: Mapping[str, Any] | list[Any] | None = None,
    *,
    status_code: int = 200,
) -> httpx.Response:
    """Build a sanitized JSON response suitable for ``MockTransport``."""
    return httpx.Response(
        status_code, json={"status": "ok"} if payload is None else payload
    )


def json_error(
    *,
    status_code: int = 400,
    status: str = "validation",
) -> httpx.Response:
    """Build a sanitized BCIC/HTTP error response."""
    return json_response({"status": status}, status_code=status_code)
