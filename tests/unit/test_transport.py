import httpx
import pytest

from bcic.exceptions import APIError, ValidationError
from bcic.transport import ResponseParser, RestTransport


def test_transport_builds_get_and_post_requests() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"status": "ok", "value": 1})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    transport = RestTransport("https://example.test/root", client=client)

    assert transport.execute("getRecord", {"id": "42"}, http_method="GET")["value"] == 1
    transport.execute("createRecord", {"name": "Ada"}, http_method="POST")

    assert requests[0].url == "https://example.test/root/rest/api/getRecord?id=42"
    assert requests[1].url == "https://example.test/root/rest/api/createRecord"
    assert requests[1].read() == b'{"name":"Ada"}'


def test_parser_normalizes_json_object() -> None:
    response = httpx.Response(200, json={"status": "ok", "items": [1, 2]})

    assert ResponseParser().parse(response, "json") == {
        "status": "ok",
        "items": [1, 2],
    }


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(200, content=b""),
        httpx.Response(200, content=b"not json"),
        httpx.Response(200, json=[1, 2]),
    ],
)
def test_parser_rejects_invalid_json_without_raw_details(
    response: httpx.Response,
) -> None:
    with pytest.raises(APIError) as error:
        ResponseParser().parse(response, "json")

    assert str(error.value) == "Invalid BCIC response"
    assert "not json" not in str(error.value)


def test_parser_rejects_unsupported_output_format() -> None:
    response = httpx.Response(200, content=b"<resp />")

    with pytest.raises(ValidationError, match="Unsupported output format"):
        ResponseParser().parse(response, "xml")


@pytest.mark.parametrize("method_name", ["", "../login", "https://evil.test", "a/b"])
def test_transport_rejects_unsafe_method_names(method_name: str) -> None:
    transport = RestTransport(
        "https://example.test",
        client=httpx.Client(transport=httpx.MockTransport(lambda request: None)),
    )

    with pytest.raises(ValidationError, match="Invalid REST method name"):
        transport.execute(method_name)
