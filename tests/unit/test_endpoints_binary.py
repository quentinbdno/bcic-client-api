import base64
import json

import httpx
import pytest

from bcic import Client
from bcic.exceptions import APIError, AuthorizationError, NotFoundError, ValidationError


def make_client(
    requests: list[httpx.Request], payload: object, *, status_code: int = 200
) -> Client:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/login"):
            return httpx.Response(200, json={"status": "ok", "sessionId": "sid"})
        return httpx.Response(status_code, json=payload)

    return Client(
        base_url="https://example.test",
        username="user",
        password="password",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_get_binary_decodes_exact_limit_and_hides_repr() -> None:
    requests: list[httpx.Request] = []
    marker = b"private-payload"
    client = make_client(
        requests,
        {
            "attachment": {
                "fileName": "proof.pdf",
                "contentType": "application/pdf",
                "fileData": base64.b64encode(marker).decode(),
            }
        },
    )
    result = client.binary.get(" Case ", " 42 ", " attachment ", max_bytes=len(marker))
    assert result.content == marker
    assert result.metadata.size == len(marker)
    assert "private-payload" not in repr(result)
    assert dict(requests[1].url.params) == {
        "objName": "Case",
        "id": "42",
        "fieldName": "attachment",
        "output": "json",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"other": {"fileName": "x", "contentType": "x", "fileData": "YQ=="}},
        {"file": {"fileName": "x", "contentType": "x"}},
        {"file": {"fileName": "x", "contentType": "x", "fileData": "***"}},
        {"file": {"fileName": "x", "contentType": "x", "fileData": ""}},
    ],
)
def test_get_binary_rejects_malformed_envelopes(payload: object) -> None:
    with pytest.raises(ValidationError) as error:
        make_client([], payload).binary.get("Object", "1", "file")
    assert "***" not in str(error.value)


def test_get_binary_rejects_oversize_without_exposing_payload() -> None:
    marker = base64.b64encode(b"private-payload").decode()
    with pytest.raises(APIError) as error:
        make_client(
            [],
            {"file": {"fileName": "x", "contentType": "x", "fileData": marker}},
        ).binary.get("Object", "1", "file", max_bytes=2)
    assert marker not in str(error.value)


@pytest.mark.parametrize(
    ("values", "limit"),
    [
        (("", "1", "file"), 1),
        (("Object", "", "file"), 1),
        (("O", "1", ""), 1),
        (("O", "1", "f"), 0),
    ],
)
def test_get_binary_rejects_input_without_network(
    values: tuple[str, str, str], limit: int
) -> None:
    requests: list[httpx.Request] = []
    with pytest.raises(ValidationError):
        make_client(requests, {}).binary.get(*values, max_bytes=limit)
    assert requests == []


@pytest.mark.parametrize(
    ("status", "exception"), [(403, AuthorizationError), (404, NotFoundError)]
)
def test_get_binary_preserves_mapped_failures(
    status: int, exception: type[Exception]
) -> None:
    with pytest.raises(exception):
        make_client([], {}, status_code=status).binary.get("O", "1", "file")


@pytest.mark.parametrize(
    "content",
    [b"abc", bytearray(b"abc"), memoryview(b"abc").toreadonly()],
)
def test_set_binary_encodes_bytes_like_content(content: object) -> None:
    requests: list[httpx.Request] = []
    result = make_client(
        requests, {"status": "ok", "message": " uploaded "}
    ).binary.set(
        "Object",
        "1",
        "file",
        content,  # type: ignore[arg-type]
        file_name="a.bin",
        content_type="application/octet-stream",
    )
    body = json.loads(requests[1].content)
    assert requests[1].method == "POST"
    assert body["value"] == "YWJj"
    assert result.message == "uploaded"
    assert not hasattr(result, "content")
    assert "YWJj" not in repr(result)


@pytest.mark.parametrize(
    ("content", "file_name", "content_type", "limit"),
    [
        (b"", "a", "type", 10),
        (b"abc", "", "type", 10),
        (b"abc", "a", "", 10),
        (b"abc", "a", "type", 2),
        ("abc", "a", "type", 10),
        (memoryview(bytearray(b"abc")), "a", "type", 10),
    ],
)
def test_set_binary_rejects_invalid_input_without_request(
    content: object, file_name: str, content_type: str, limit: int
) -> None:
    requests: list[httpx.Request] = []
    with pytest.raises(ValidationError):
        make_client(requests, {}).binary.set(
            "O",
            "1",
            "f",
            content,  # type: ignore[arg-type]
            file_name=file_name,
            content_type=content_type,
            max_bytes=limit,
        )
    assert requests == []


@pytest.mark.parametrize(
    ("payload", "exception"),
    [
        ([], ValidationError),
        ({}, ValidationError),
        ({"status": ""}, APIError),
        ({"status": "ok", "message": 1}, ValidationError),
    ],
)
def test_set_binary_rejects_malformed_success(
    payload: object, exception: type[Exception]
) -> None:
    with pytest.raises(exception):
        make_client([], payload).binary.set(
            "O", "1", "f", b"secret", file_name="a", content_type="type"
        )
