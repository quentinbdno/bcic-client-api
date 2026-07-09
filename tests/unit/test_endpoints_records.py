import json
from collections.abc import Callable

import httpx
import pytest

from bcic import Client
from bcic.exceptions import (
    APIError,
    AuthorizationError,
    NotFoundError,
    PaginationLimitError,
    ServerError,
    ValidationError,
)
from bcic.pagination import EqualityFilter

ResponseFactory = Callable[[httpx.Request], httpx.Response]


def make_client(
    requests: list[httpx.Request], response_factory: ResponseFactory
) -> Client:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/login"):
            return httpx.Response(200, json={"status": "ok", "sessionId": "sid"})
        return response_factory(request)

    return Client(
        base_url="https://example.test",
        username="user",
        password="password",
        retry_wait_seconds=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def test_get_record_reuses_auth_and_normalizes_dynamic_fields() -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        lambda request: httpx.Response(
            200,
            json={"objName": "Contact", "id": 42, "name": "Ada", "active": True},
        ),
    )

    record = client.records.get(
        " Contact ", " 42 ", field_names=["name", "active"], composite=1
    )

    assert record.object_name == "Contact"
    assert record.record_id == "42"
    assert record.fields == {"name": "Ada", "active": True}
    assert requests[1].headers["sessionid"] == "sid"
    assert dict(requests[1].url.params) == {
        "objNames": "Contact",
        "id": "42",
        "composite": "1",
        "fieldList": "name,active",
        "output": "json",
    }


@pytest.mark.parametrize(
    ("object_name", "record_id", "field_names", "composite"),
    [
        ("", "1", None, 0),
        ("Contact", " ", None, 0),
        ("Contact", "1", [], 0),
        ("Contact", "1", [" "], 0),
        ("Contact", "1", None, -1),
        ("Contact", "1", None, True),
    ],
)
def test_get_rejects_invalid_input_without_network(
    object_name: str,
    record_id: str,
    field_names: list[str] | None,
    composite: int,
) -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests, lambda request: httpx.Response(500))

    with pytest.raises(ValidationError):
        client.records.get(
            object_name,
            record_id,
            field_names=field_names,
            composite=composite,
        )

    assert requests == []


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"objName": "Contact"},
        {"objName": "Other", "id": "42"},
        {"objName": "Contact", "id": "42", "bad": object()},
    ],
)
def test_get_rejects_malformed_or_mismatched_response(payload: object) -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests, lambda request: httpx.Response(200, json=payload))

    with pytest.raises((ValidationError, TypeError)):
        client.records.get("Contact", "42")


def test_get_maps_missing_record() -> None:
    client = make_client([], lambda request: httpx.Response(404))

    with pytest.raises(NotFoundError):
        client.records.get("Contact", "missing")


def test_get_page_maps_options_and_normalizes_array_atomically() -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        lambda request: httpx.Response(
            200,
            json=[
                {"objName": "Contact", "id": "1", "name": "Ada"},
                {"objName": "Contact", "id": "2", "name": "Grace"},
            ],
        ),
    )

    page = client.records.get_page(
        "view-1",
        start_row=2,
        page_size=2,
        object_names=["Contact"],
        field_names=["name"],
        equality_filter=EqualityFilter(name="active", value="true"),
        only_view_fields=True,
    )

    assert [record.record_id for record in page.items] == ["1", "2"]
    assert page.metadata.start_row == 2
    assert page.metadata.returned_count == 2
    assert page.metadata.has_more is True
    assert page.metadata.total_items is None
    assert requests[1].url.params["filterName"] == "active"
    assert requests[1].url.params["filterValue"] == "true"


def test_get_page_uses_authoritative_mapping_metadata() -> None:
    client = make_client(
        [],
        lambda request: httpx.Response(
            200,
            json={
                "records": [{"objName": "Contact", "id": "1"}],
                "totalItems": 3,
                "hasMore": False,
            },
        ),
    )

    page = client.records.get_page("view", page_size=2)

    assert page.metadata.total_items == 3
    assert page.metadata.total_pages == 2
    assert page.metadata.has_more is False


def test_get_page_rejects_whole_page_when_one_record_is_invalid() -> None:
    client = make_client(
        [],
        lambda request: httpx.Response(
            200,
            json=[
                {"objName": "Contact", "id": "1"},
                {"objName": "Contact"},
            ],
        ),
    )

    with pytest.raises(ValidationError):
        client.records.get_page("view")


def test_list_all_advances_offsets_without_replaying_pages() -> None:
    requests: list[httpx.Request] = []

    def response(request: httpx.Request) -> httpx.Response:
        start = int(request.url.params["startRow"])
        records = (
            [
                {"objName": "Contact", "id": str(start + 1)},
                {"objName": "Contact", "id": str(start + 2)},
            ]
            if start < 4
            else []
        )
        return httpx.Response(200, json=records)

    client = make_client(requests, response)
    records = client.records.list_all("view", page_size=2, max_pages=4, max_items=10)

    assert [record.record_id for record in records] == ["1", "2", "3", "4"]
    assert [request.url.params["startRow"] for request in requests[1:]] == [
        "0",
        "2",
        "4",
    ]


def test_list_all_raises_instead_of_truncating_at_limits() -> None:
    client = make_client(
        [],
        lambda request: httpx.Response(
            200,
            json=[
                {"objName": "Contact", "id": "1"},
                {"objName": "Contact", "id": "2"},
            ],
        ),
    )

    with pytest.raises(PaginationLimitError):
        client.records.list_all("view", page_size=2, max_pages=1, max_items=10)

    with pytest.raises(PaginationLimitError):
        client.records.list_all("view", page_size=2, max_pages=2, max_items=1)


def test_create_flattens_validated_fields_and_returns_identity() -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        lambda request: httpx.Response(
            200, json={"status": "ok", "objName": "Contact", "id": 7}
        ),
    )

    result = client.records.create(
        "Contact", {"name": "Ada", "active": True}, use_ids=True
    )

    assert result.record_id == "7"
    assert json.loads(requests[1].content) == {
        "objName": "Contact",
        "useIds": True,
        "name": "Ada",
        "active": True,
        "output": "json",
    }


@pytest.mark.parametrize(
    "fields",
    [{}, {"": "value"}, {"OUTPUT": "xml"}, {"field": object()}],
)
def test_create_rejects_invalid_fields_without_exposing_values(
    fields: dict[str, object],
) -> None:
    requests: list[httpx.Request] = []
    client = make_client(requests, lambda request: httpx.Response(500))

    with pytest.raises(ValidationError) as error:
        client.records.create("Contact", fields)  # type: ignore[arg-type]

    assert requests == []
    assert "value" not in str(error.value)


def test_update_sends_only_supplied_changes_and_returns_status() -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        lambda request: httpx.Response(
            200, json={"status": "success", "Msg": "Updated"}
        ),
    )

    result = client.records.update("Contact", "42", {"name": "Grace"})

    assert result.status == "success"
    assert result.message == "Updated"
    assert json.loads(requests[1].content) == {
        "objName": "Contact",
        "id": "42",
        "useIds": False,
        "name": "Grace",
        "output": "json",
    }


def test_delete_uses_get_and_documents_recycle_bin_semantics() -> None:
    requests: list[httpx.Request] = []
    client = make_client(
        requests,
        lambda request: httpx.Response(200, json={"status": "ok", "Msg": "Deleted"}),
    )

    result = client.records.delete("Contact", "42")

    assert result.status == "ok"
    assert requests[1].method == "GET"
    assert dict(requests[1].url.params) == {
        "objName": "Contact",
        "id": "42",
        "output": "json",
    }
    assert "Recycle Bin" in (type(client.records).delete.__doc__ or "")


@pytest.mark.parametrize(
    ("status", "exception"),
    [
        (400, ValidationError),
        (403, AuthorizationError),
        (404, NotFoundError),
        (500, ServerError),
    ],
)
def test_record_writes_map_http_failures(
    status: int, exception: type[Exception]
) -> None:
    client = make_client([], lambda request: httpx.Response(status))

    with pytest.raises(exception):
        client.records.delete("Contact", "42")


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_status_operations_reject_malformed_success(operation: str) -> None:
    client = make_client([], lambda request: httpx.Response(200, json={"value": 1}))

    with pytest.raises(APIError):
        if operation == "update":
            client.records.update("Contact", "42", {"name": "Ada"})
        else:
            client.records.delete("Contact", "42")
