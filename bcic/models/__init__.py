"""Public typed model foundations."""

from bcic.models.common import Page, PageMetadata, ResponseMetadata
from bcic.models.records import (
    CreateRecordRequest,
    DynamicRecord,
    JSONScalar,
    JSONValue,
    RecordCreationResult,
    RecordDeletionResult,
    RecordUpdateResult,
    UpdateRecordRequest,
)

__all__ = [
    "CreateRecordRequest",
    "DynamicRecord",
    "JSONScalar",
    "JSONValue",
    "Page",
    "PageMetadata",
    "RecordCreationResult",
    "RecordDeletionResult",
    "RecordUpdateResult",
    "ResponseMetadata",
    "UpdateRecordRequest",
]
