import httpx
import pytest

from bcic import Client
from bcic.exceptions import APIError


def make_client(
    requests: list[httpx.Request],
    *,
    fail_logout: bool = False,
) -> tuple[Client, httpx.Client]:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/login"):
            return httpx.Response(200, json={"status": "ok", "sessionId": "sid"})
        if fail_logout and request.url.path.endswith("/logout"):
            return httpx.Response(200, content=b"bad-json")
        return httpx.Response(200, json={"status": "ok"})

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    return (
        Client(
            base_url="https://example.test",
            username="user",
            password="password",
            http_client=http_client,
        ),
        http_client,
    )


def test_logout_calls_api_once_and_is_idempotent() -> None:
    requests: list[httpx.Request] = []
    client, _ = make_client(requests)
    client.authenticate()

    client.logout()
    client.logout()

    assert [request.url.path for request in requests] == [
        "/rest/api/login",
        "/rest/api/logout",
    ]
    assert requests[1].headers["sessionid"] == "sid"


def test_logout_clears_state_even_when_remote_response_fails() -> None:
    requests: list[httpx.Request] = []
    client, _ = make_client(requests, fail_logout=True)
    client.authenticate()

    with pytest.raises(APIError):
        client.logout()
    client.logout()

    assert len(requests) == 2


def test_close_is_idempotent_and_does_not_close_injected_client() -> None:
    requests: list[httpx.Request] = []
    client, http_client = make_client(requests)

    client.close()
    client.close()

    assert not http_client.is_closed
    with pytest.raises(APIError, match="Client is closed"):
        client.authenticate()


def test_context_manager_closes_and_preserves_body_exception() -> None:
    requests: list[httpx.Request] = []
    client, _ = make_client(requests)

    with pytest.raises(RuntimeError, match="body failure"):
        with client as entered:
            assert entered is client
            raise RuntimeError("body failure")

    with pytest.raises(APIError, match="Client is closed"):
        client.authenticate()
