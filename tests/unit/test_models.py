import math
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
    assert page.items == (record,)
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


def test_dynamic_record_rejects_non_finite_json_values() -> None:
    with pytest.raises(ValidationError):
        DynamicRecord(
            object_name="Contact",
            record_id="42",
            fields={"score": math.inf},
        )


def test_dynamic_record_rejects_blank_identity_values() -> None:
    with pytest.raises(ValidationError):
        DynamicRecord(object_name=" ", record_id="42", fields={})

    with pytest.raises(ValidationError):
        DynamicRecord(object_name="Contact", record_id="\t", fields={})


def test_strict_models_reject_coerced_field_types() -> None:
    with pytest.raises(ValidationError):
        ResponseMetadata(status=1)


def test_frozen_models_do_not_expose_mutable_nested_collections() -> None:
    record = DynamicRecord(
        object_name="Contact",
        record_id="42",
        fields={"tags": ["primary"], "address": {"city": "Paris"}},
    )
    page = Page[DynamicRecord](
        items=[record],
        metadata=PageMetadata(page=1, page_size=20),
    )

    with pytest.raises(TypeError):
        page.items[0] = record
    with pytest.raises(TypeError):
        record.fields["new"] = "value"
    with pytest.raises(AttributeError):
        record.fields["tags"].append("secondary")  # type: ignore[attr-defined, union-attr]
    with pytest.raises(TypeError):
        record.fields["address"]["city"] = "Lyon"  # type: ignore[index]


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
