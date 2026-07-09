"""Typed record paging options and bounded traversal."""

from collections.abc import Callable

from pydantic import Field, field_validator

from bcic.exceptions import PaginationLimitError, ValidationError
from bcic.models.common import Page, SDKModel


class EqualityFilter(SDKModel):
    """A safe named equality filter for BCIC view paging."""

    name: str
    value: str

    @field_validator("name", "value", mode="before")
    @classmethod
    def require_text(cls, value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("must be non-empty text")
        return value.strip()


class RecordPageOptions(SDKModel):
    """Validated options for one REST v1 ``getPage`` request."""

    view_id: str
    start_row: int = Field(default=0, ge=0)
    page_size: int = Field(default=100, gt=0)
    composite: int = Field(default=0, ge=0)
    object_names: tuple[str, ...] | None = None
    field_names: tuple[str, ...] | None = None
    equality_filter: EqualityFilter | None = None
    only_view_fields: bool = False

    @field_validator("view_id", mode="before")
    @classmethod
    def require_view_id(cls, value: object) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("view_id must be non-empty")
        return value.strip()

    @field_validator("object_names", "field_names", mode="before")
    @classmethod
    def normalize_names(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, list | tuple) or not value:
            raise ValueError("names must be a non-empty sequence")
        normalized: list[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise ValueError("names must contain non-empty text")
            normalized.append(item.strip())
        return tuple(normalized)


def traverse_pages[T](
    fetch_page: Callable[[int], Page[T]],
    *,
    page_size: int,
    max_pages: int,
    max_items: int,
) -> list[T]:
    """Fetch complete pages eagerly, raising instead of truncating."""
    if page_size <= 0 or max_pages <= 0 or max_items <= 0:
        raise ValidationError("Pagination limits must be positive")
    items: list[T] = []
    requested_offsets: set[int] = set()
    offset = 0
    pages = 0
    while True:
        if pages >= max_pages:
            raise PaginationLimitError("Maximum page limit reached")
        if offset in requested_offsets:
            raise ValidationError("Pagination did not advance")
        requested_offsets.add(offset)
        page = fetch_page(offset)
        pages += 1
        metadata = page.metadata
        if metadata.start_row != offset:
            raise ValidationError("Pagination did not advance")
        if len(items) + len(page.items) > max_items:
            raise PaginationLimitError("Maximum item limit reached")
        items.extend(page.items)
        if not page.items or len(page.items) < page_size or metadata.has_more is False:
            return items
        next_offset = offset + page_size
        if next_offset <= offset:
            raise ValidationError("Pagination did not advance")
        offset = next_offset
