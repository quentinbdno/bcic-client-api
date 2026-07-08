"""Reusable response and pagination model contracts."""

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from pydantic import (
    ValidationError as PydanticValidationError,
)

from bcic.exceptions import ValidationError


class SDKModel(BaseModel):
    """Strict immutable model with a sanitized SDK validation boundary."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    def __init__(self, **data: object) -> None:
        try:
            super().__init__(**data)
        except PydanticValidationError as error:
            name = type(self).__name__
            raise ValidationError(f"Invalid {name} data") from error


class ResponseMetadata(SDKModel):
    """Common optional metadata accompanying a BCIC response."""

    status: str | None = None
    message: str | None = None
    request_id: str | None = None


class PageMetadata(SDKModel):
    """Validated pagination state for a single response page."""

    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class Page[T](SDKModel):
    """A typed page of SDK results and its pagination metadata."""

    items: list[T]
    metadata: PageMetadata
