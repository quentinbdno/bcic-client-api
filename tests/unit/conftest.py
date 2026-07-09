"""Shared deterministic fixtures for unit tests."""

from collections.abc import Callable, Iterator

import httpx
import pytest

from bcic import Client
from tests.unit.fakes import RequestRecorder, ResponseFactory, json_response

TEST_BASE_URL = "https://sdk-fixture.example.test"
TEST_USERNAME = "fixture-user"
TEST_PASSWORD = "fixture-password"


@pytest.fixture(autouse=True)
def no_live_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail clearly if code attempts to use httpx's live HTTP transport."""

    def reject_network(
        _transport: httpx.HTTPTransport, request: httpx.Request
    ) -> httpx.Response:
        raise AssertionError(
            "Live HTTP is disabled in unit tests; inject httpx.MockTransport "
            f"for {request.method} {request.url.path}"
        )

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", reject_network)


@pytest.fixture
def client_factory() -> Iterator[
    Callable[[ResponseFactory | None], tuple[Client, RequestRecorder]]
]:
    """Construct configured clients with an ordered request recorder."""
    clients: list[httpx.Client] = []

    def create(
        responder: ResponseFactory | None = None,
    ) -> tuple[Client, RequestRecorder]:
        recorder = RequestRecorder(responder or (lambda _: json_response()))
        http_client = httpx.Client(transport=httpx.MockTransport(recorder))
        clients.append(http_client)
        return (
            Client(
                base_url=TEST_BASE_URL,
                username=TEST_USERNAME,
                password=TEST_PASSWORD,
                retry_wait_seconds=0,
                http_client=http_client,
            ),
            recorder,
        )

    yield create
    for client in clients:
        client.close()
