import httpx
import pytest

from bcic import Client
from bcic.exceptions import ValidationError


def make_client(requests: list[httpx.Request]) -> Client:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/login"):
            return httpx.Response(200, json={"status": "ok", "sessionId": "sid"})
        return httpx.Response(200, json={"status": "ok", "value": 42})

    return Client(
        base_url="https://example.test",
        username="user",
        password="password",
        retry_wait_seconds=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_generic_methods_execute_get_and_post_through_shared_transport() -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests)

    get_result = client.methods.execute("getRecord", {"id": "42"})
    post_result = client.methods.execute(
        "createRecord", {"name": "Ada"}, http_method="POST"
    )

    assert get_result["value"] == 42
    assert post_result["value"] == 42
    assert requests[1].url == (
        "https://example.test/rest/api/getRecord?id=42&output=json"
    )
    assert requests[2].read() == b'{"name":"Ada","output":"json"}'
    assert requests[1].headers["sessionid"] == "sid"


@pytest.mark.parametrize(
    ("method_name", "parameters", "http_method", "output_format"),
    [
        ("../login", {}, "GET", None),
        ("getRecord", {"nested": object()}, "GET", None),
        ("getRecord", {}, "DELETE", None),
        ("getRecord", {}, "GET", "yaml"),
    ],
)
def test_generic_methods_reject_invalid_input_before_network(
    method_name: str,
    parameters: object,
    http_method: str,
    output_format: str | None,
) -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests)

    with pytest.raises(ValidationError):
        client.methods.execute(
            method_name,
            parameters,  # type: ignore[arg-type]
            http_method=http_method,  # type: ignore[arg-type]
            output_format=output_format,  # type: ignore[arg-type]
        )

    assert requests == []


def test_methods_endpoint_documents_lower_level_role() -> None:
    assert "lower-level" in (type(make_client([]).methods).execute.__doc__ or "")
    assert "domain" in (type(make_client([]).methods).execute.__doc__ or "")
