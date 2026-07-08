"""Typed dynamic BCIC record foundation."""

from pydantic import Field

from bcic.models.common import SDKModel

type JSONScalar = str | int | float | bool | None
type JSONValue = JSONScalar | list[JSONValue] | dict[str, JSONValue]


class DynamicRecord(SDKModel):
    """BCIC record identity plus deliberately dynamic JSON-compatible fields."""

    object_name: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    fields: dict[str, JSONValue]
