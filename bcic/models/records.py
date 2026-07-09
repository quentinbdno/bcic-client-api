"""Typed request, response, and normalization models for BCIC records."""

import math
from collections.abc import Mapping
from typing import cast

from pydantic import Field, field_validator

from bcic.exceptions import ValidationError
from bcic.models.common import SDKModel

type JSONScalar = str | int | float | bool | None
type JSONValue = JSONScalar | list[JSONValue] | dict[str, JSONValue]

_RESERVED_FIELD_NAMES = frozenset({"objname", "id", "useids", "output", "sessionid"})


def is_json_value(value: object) -> bool:
    """Return whether a value is recursively JSON-compatible."""
    if value is None or isinstance(value, str | bool | int):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and is_json_value(item) for key, item in value.items()
        )
    return False


def validate_identifier(value: object, label: str) -> str:
    """Normalize one required public record identifier."""
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"Invalid {label}")
    return value.strip()


def validate_dynamic_fields(
    value: object, *, label: str, require_non_empty: bool = True
) -> dict[str, JSONValue]:
    """Validate dynamic fields without including their values in errors."""
    if not isinstance(value, Mapping) or (require_non_empty and not value):
        raise ValidationError(f"Invalid {label}")
    result: dict[str, JSONValue] = {}
    for key, item in value.items():
        if (
            not isinstance(key, str)
            or not key.strip()
            or key.casefold() in _RESERVED_FIELD_NAMES
            or not is_json_value(item)
        ):
            raise ValidationError(f"Invalid {label}")
        result[key] = cast(JSONValue, item)
    return result


class DynamicRecord(SDKModel):
    """BCIC record identity plus deliberately dynamic JSON-compatible fields."""

    object_name: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    fields: dict[str, JSONValue]


def normalize_record(
    payload: object,
    *,
    expected_object_name: str | None = None,
    expected_record_id: str | None = None,
) -> DynamicRecord:
    """Normalize a documented BCIC record mapping atomically."""
    if not isinstance(payload, Mapping):
        raise ValidationError("Invalid record response")
    object_name = payload.get("objName")
    record_id = payload.get("id")
    if not isinstance(object_name, str) or not object_name.strip():
        raise ValidationError("Invalid record response")
    if not isinstance(record_id, str | int) or not str(record_id).strip():
        raise ValidationError("Invalid record response")
    normalized_object = object_name.strip()
    normalized_id = str(record_id).strip()
    if (
        expected_object_name is not None and normalized_object != expected_object_name
    ) or (expected_record_id is not None and normalized_id != expected_record_id):
        raise ValidationError("Record response identity mismatch")
    fields = {
        key: value for key, value in payload.items() if key not in {"objName", "id"}
    }
    if not all(
        isinstance(key, str) and is_json_value(value) for key, value in fields.items()
    ):
        raise ValidationError("Invalid record response")
    return DynamicRecord(
        object_name=normalized_object,
        record_id=normalized_id,
        fields=cast(dict[str, JSONValue], fields),
    )


class CreateRecordRequest(SDKModel):
    """Validated immutable input for record creation."""

    object_name: str
    fields: dict[str, JSONValue]
    use_ids: bool = False

    @field_validator("object_name", mode="before")
    @classmethod
    def normalize_object_name(cls, value: object) -> str:
        return validate_identifier(value, "object name")

    @field_validator("fields", mode="before")
    @classmethod
    def normalize_fields(cls, value: object) -> dict[str, JSONValue]:
        return validate_dynamic_fields(value, label="record fields")


class UpdateRecordRequest(SDKModel):
    """Validated immutable input for a partial record update."""

    object_name: str
    record_id: str
    changes: dict[str, JSONValue]
    use_ids: bool = False

    @field_validator("object_name", mode="before")
    @classmethod
    def normalize_object_name(cls, value: object) -> str:
        return validate_identifier(value, "object name")

    @field_validator("record_id", mode="before")
    @classmethod
    def normalize_record_id(cls, value: object) -> str:
        return validate_identifier(value, "record ID")

    @field_validator("changes", mode="before")
    @classmethod
    def normalize_changes(cls, value: object) -> dict[str, JSONValue]:
        return validate_dynamic_fields(value, label="record changes")


class RecordCreationResult(SDKModel):
    """Identity returned after successful record creation."""

    object_name: str = Field(min_length=1)
    record_id: str = Field(min_length=1)


class RecordUpdateResult(SDKModel):
    """Status returned after a successful partial record update."""

    object_name: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    status: str = Field(min_length=1)
    message: str | None = None


class RecordDeletionResult(SDKModel):
    """Status returned after a successful record deletion request."""

    object_name: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    status: str = Field(min_length=1)
    message: str | None = None
