"""Payload-safe binary result models."""

from pydantic import Field

from bcic.models.common import SDKModel


class BinaryMetadata(SDKModel):
    """Metadata accompanying decoded BCIC binary content."""

    object_name: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    field_name: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    content_type: str = Field(min_length=1)
    size: int = Field(ge=1)


class BinaryData(SDKModel):
    """Decoded attachment whose representation deliberately omits bytes."""

    content: bytes = Field(repr=False)
    metadata: BinaryMetadata


class BinaryUploadResult(SDKModel):
    """Content-free result of a binary upload."""

    object_name: str = Field(min_length=1)
    record_id: str = Field(min_length=1)
    field_name: str = Field(min_length=1)
    status: str = Field(min_length=1)
    message: str | None = None
