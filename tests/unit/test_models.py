from collections.abc import Callable

import pytest

from bcic.exceptions import ValidationError
from bcic.models import DynamicRecord, Page, PageMetadata, ResponseMetadata


def test_common_metadata_and_generic_page_are_typed_models() -> None:
    metadata = ResponseMetadata(status="success", message="ok", request_id="req-1")
    page_metadata = PageMetadata(page=1, page_size=20, total_items=1, total_pages=1)
    record = DynamicRecord(
        object_name="Contact",
        record_id="42",
        fields={"name": "Ada", "active": True, "score": 3.5},
    )
    page = Page[DynamicRecord](items=[record], metadata=page_metadata)

    assert metadata.model_dump()["request_id"] == "req-1"
    assert page.items == [record]
    assert page.metadata.total_items == 1


def test_dynamic_record_supports_recursive_json_values() -> None:
    record = DynamicRecord(
        object_name="Contact",
        record_id="42",
        fields={
            "tags": ["primary", None],
            "address": {"city": "Paris", "verified": False},
        },
    )

    assert record.fields["address"] == {"city": "Paris", "verified": False}


@pytest.mark.parametrize(
    "factory",
    [
        lambda: PageMetadata(page=0, page_size=20, total_items=1, total_pages=1),
        lambda: DynamicRecord(object_name="", record_id="42", fields={}),
        lambda: DynamicRecord(
            object_name="Contact", record_id="42", fields={"invalid": object()}
        ),
    ],
)
def test_invalid_model_data_raises_sanitized_sdk_error(
    factory: Callable[[], object],
) -> None:
    with pytest.raises(ValidationError) as error:
        factory()

    assert str(error.value).startswith("Invalid ")
    assert "object at" not in str(error.value)
