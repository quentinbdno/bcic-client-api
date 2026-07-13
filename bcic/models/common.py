"""Reusable response and pagination model contracts."""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)
from pydantic import (
    ValidationError as PydanticValidationError,
)

from bcic.exceptions import ValidationError
from bcic.utils.logging import sanitize_context


class SDKModel(BaseModel):
    """Strict immutable model with a sanitized SDK validation boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    def __init__(self, **data: object) -> None:
        try:
            super().__init__(**data)
        except PydanticValidationError as error:
            name = type(self).__name__
            raise ValidationError(f"Invalid {name} data") from error

    def __repr__(self) -> str:
        """Return a useful representation with sensitive fields redacted."""
        fields = sanitize_context(self.model_dump())
        return f"{type(self).__name__}({fields!r})"

    def __str__(self) -> str:
        """Return the same sanitized text used for debugging representation."""
        return repr(self)


class ResponseMetadata(SDKModel):
    """Common optional metadata accompanying a BCIC response."""

    status: str | None = None
    message: str | None = None
    request_id: str | None = None


class PageMetadata(SDKModel):
    """Validated pagination state for a single response page."""

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    start_row: int = Field(default=0, ge=0)
    returned_count: int = Field(default=0, ge=0)
    has_more: bool | None = None
    total_items: int | None = Field(default=None, ge=0)
    total_pages: int | None = Field(default=None, ge=0)


class Page[T](SDKModel):
    """A typed page of SDK results and its pagination metadata."""

    items: tuple[T, ...]
    metadata: PageMetadata

    @field_validator("items", mode="before")
    @classmethod
    def freeze_items(cls, value: object) -> object:
        """Store page items immutably while accepting ordinary sequences."""
        if isinstance(value, list | tuple):
            return tuple(value)
        return value
