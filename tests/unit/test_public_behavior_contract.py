"""Cross-component public behavior and sensitive-value contracts."""

import logging

import httpx
import pytest

from bcic import Client
from bcic.exceptions import BCICError
from bcic.models.binary import BinaryData, BinaryMetadata
from bcic.models.records import DynamicRecord

SENSITIVE_MARKERS = (
    "credential-marker",
    "session-marker",
    "token-marker",
    "raw-bytes-marker",
    "cmF3LWJ5dGVzLW1hcmtlcg==",
)


@pytest.mark.parametrize(
    "model",
    [
        DynamicRecord(
            object_name="Contact",
            record_id="1",
            fields={
                "credential": SENSITIVE_MARKERS[0],
                "sessionId": SENSITIVE_MARKERS[1],
                "token": SENSITIVE_MARKERS[2],
                "notes": SENSITIVE_MARKERS[2],
                "attachment": SENSITIVE_MARKERS[4],
            },
        ),
        BinaryData(
            content=SENSITIVE_MARKERS[3].encode(),
            metadata=BinaryMetadata(
                object_name="Contact",
                record_id="1",
                field_name="Attachment",
                file_name="fixture.bin",
                content_type="application/octet-stream",
                size=16,
            ),
        ),
    ],
)
def test_public_model_repr_does_not_expose_sensitive_values(model: object) -> None:
    representation = repr(model) + str(model)
    assert all(marker not in representation for marker in SENSITIVE_MARKERS)


@pytest.mark.parametrize(
    ("failure", "expected"),
    [
        (httpx.ConnectError("credential-marker"), BCICError),
        (httpx.ReadTimeout("token-marker"), BCICError),
    ],
    ids=["network-error", "timeout"],
)
def test_client_boundary_never_exposes_raw_httpx_failures(
    failure: Exception,
    expected: type[BCICError],
) -> None:
    client = Client(
        base_url="https://sdk-fixture.example.test",
        username="fixture-user",
        password="fixture-password",
        max_retries=0,
        http_client=httpx.Client(
            transport=httpx.MockTransport(lambda _: (_ for _ in ()).throw(failure))
        ),
    )

    with pytest.raises(expected) as error:
        client.records.get("Contact", "1")

    assert not isinstance(error.value, httpx.HTTPError)
    assert all(marker not in str(error.value) for marker in SENSITIVE_MARKERS)


def test_cross_component_failure_is_sanitized_in_logs_and_error(
    client_factory: object,
    caplog: pytest.LogCaptureFixture,
) -> None:
    create = client_factory
    assert callable(create)

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/login"):
            return httpx.Response(
                200, json={"status": "ok", "sessionId": SENSITIVE_MARKERS[1]}
            )
        return httpx.Response(
            403, json={"status": "permission", "err": SENSITIVE_MARKERS[2]}
        )

    client, _ = create(handler)
    caplog.set_level(logging.DEBUG)
    with pytest.raises(BCICError) as error:
        client.users.get_role("role-1")

    combined = caplog.text + str(error.value)
    assert all(marker not in combined for marker in SENSITIVE_MARKERS)
