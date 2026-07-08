import httpx
import pytest

from bcic import Client
from bcic.auth import SessionAuth
from bcic.config import ClientConfig
from bcic.exceptions import AuthenticationError
from bcic.transport import RestTransport


def config() -> ClientConfig:
    return ClientConfig(
        base_url="https://example.test",
        username="integration-user",
        password="secret-value",
    )


def test_explicit_authentication_uses_headers_and_keeps_session_private() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"status": "ok", "sessionId": "private-id"})

    transport = RestTransport(
        config().base_url,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    auth = SessionAuth(config(), transport)
    transport.authentication = auth

    auth.authenticate()

    assert requests[0].url == "https://example.test/rest/api/login"
    assert requests[0].headers["loginname"] == "integration-user"
    assert requests[0].headers["password"] == "secret-value"
    assert requests[0].read() == b'{"output":"json"}'
    assert not hasattr(auth, "session_id")
    assert "private-id" not in repr(auth)


def test_lazy_authentication_occurs_once_and_attaches_session_header() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/login"):
            return httpx.Response(200, json={"status": "ok", "sessionId": "sid-1"})
        return httpx.Response(200, json={"status": "ok"})

    transport = RestTransport(
        config().base_url,
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    auth = SessionAuth(config(), transport)
    transport.authentication = auth

    transport.execute("getRecord")
    transport.execute("getRoles")

    assert [request.url.path for request in requests] == [
        "/rest/api/login",
        "/rest/api/getRecord",
        "/rest/api/getRoles",
    ]
    assert requests[1].headers["sessionid"] == "sid-1"
    assert requests[2].headers["sessionid"] == "sid-1"


@pytest.mark.parametrize(
    "payload",
    [
        {"status": "login", "err": "bad credentials"},
        {"status": "ok"},
        {"status": "ok", "sessionId": ""},
    ],
)
def test_authentication_failures_are_sanitized(payload: dict[str, str]) -> None:
    transport = RestTransport(
        config().base_url,
        client=httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=payload)
            )
        ),
    )
    auth = SessionAuth(config(), transport)

    with pytest.raises(AuthenticationError) as error:
        auth.authenticate()

    assert str(error.value) == "BCIC authentication failed"
    assert "secret-value" not in str(error.value)
    assert "bad credentials" not in str(error.value)


def test_client_exposes_explicit_authenticate() -> None:
    http_client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, json={"status": "ok", "sessionId": "sid"}
            )
        )
    )
    client = Client(
        base_url="https://example.test",
        username="user",
        password="password",
        http_client=http_client,
    )

    assert client.authenticate() is None
    assert not hasattr(client, "session_id")
