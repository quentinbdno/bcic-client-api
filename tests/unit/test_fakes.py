"""Contract tests for shared offline HTTP test infrastructure."""

import httpx
import pytest

from tests.unit.fakes import SequenceHandler, json_error, json_response


def test_client_factory_records_ordered_request_details(client_factory: object) -> None:
    create = client_factory
    assert callable(create)
    client, recorder = create(
        SequenceHandler(
            [
                json_response({"status": "ok", "sessionId": "fixture-session"}),
                json_response({"status": "ok", "value": 7}),
            ]
        )
    )

    result = client.methods.execute(
        "sampleMethod", {"query": "value"}, http_method="POST"
    )

    assert result["value"] == 7
    assert [request.url.path for request in recorder.requests] == [
        "/rest/api/login",
        "/rest/api/sampleMethod",
    ]
    assert recorder.requests[0].headers["loginname"] == "fixture-user"
    assert recorder.requests[1].headers["sessionid"] == "fixture-session"
    assert recorder.requests[1].read() == b'{"query":"value","output":"json"}'


def test_sequence_handler_rejects_unexpected_extra_request() -> None:
    handler = SequenceHandler([json_response()])
    client = httpx.Client(transport=httpx.MockTransport(handler))
    client.get("https://sdk-fixture.example.test/first")

    with pytest.raises(
        AssertionError, match=r"Unexpected HTTP request #2: GET /second"
    ):
        client.get("https://sdk-fixture.example.test/second")


def test_response_builders_are_sanitized() -> None:
    assert json_response().json() == {"status": "ok"}
    assert json_error(status_code=403).json() == {"status": "validation"}


def test_live_http_guard_fails_with_actionable_message() -> None:
    with httpx.Client() as client:
        with pytest.raises(AssertionError, match="inject httpx.MockTransport"):
            client.get("https://sdk-fixture.example.test/blocked")
