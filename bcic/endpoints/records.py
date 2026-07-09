"""Typed high-level record operations."""

from collections.abc import Mapping, Sequence
from typing import cast

from bcic.endpoints.base import BaseEndpoint
from bcic.exceptions import APIError, ValidationError
from bcic.models.common import Page, PageMetadata
from bcic.models.records import (
    CreateRecordRequest,
    DynamicRecord,
    JSONValue,
    RecordCreationResult,
    RecordDeletionResult,
    RecordUpdateResult,
    UpdateRecordRequest,
    normalize_record,
    validate_identifier,
)
from bcic.pagination import EqualityFilter, RecordPageOptions, traverse_pages
from bcic.transport import HTTPMethod


class RecordsEndpoint(BaseEndpoint):
    """Typed entry point for record retrieval and mutation."""

    REST_METHODS = (
        "getRecord",
        "getPage",
        "createRecord",
        "updateRecord",
        "deleteRecord",
    )

    def _execute(
        self,
        method_name: str,
        parameters: Mapping[str, JSONValue],
        *,
        http_method: HTTPMethod = "GET",
    ) -> dict[str, JSONValue] | list[JSONValue]:
        payload = dict(parameters)
        payload["output"] = self._context.config.output_format
        return self._context.transport.transport.execute(
            method_name,
            payload,
            http_method=http_method,
            output_format=self._context.config.output_format,
        )

    def get(
        self,
        object_name: str,
        record_id: str,
        *,
        field_names: Sequence[str] | None = None,
        composite: int = 0,
    ) -> DynamicRecord:
        """Retrieve one record.

        Args:
            object_name: BCIC object name.
            record_id: Record identifier.
            field_names: Optional fields to request.
            composite: Non-negative composite expansion depth.

        Returns:
            The atomically validated dynamic record.

        Raises:
            ValidationError: If input or response data is invalid.
            BCICError: For mapped authentication, permission, or API failures.
        """
        object_name = validate_identifier(object_name, "object name")
        record_id = validate_identifier(record_id, "record ID")
        if (
            not isinstance(composite, int)
            or isinstance(composite, bool)
            or composite < 0
        ):
            raise ValidationError("Invalid composite depth")
        parameters: dict[str, JSONValue] = {
            "objNames": object_name,
            "id": record_id,
            "composite": composite,
        }
        if field_names is not None:
            parameters["fieldList"] = _join_names(field_names, "field names")
        payload = self._execute("getRecord", parameters)
        return normalize_record(
            payload,
            expected_object_name=object_name,
            expected_record_id=record_id,
        )

    def get_page(
        self,
        view_id: str,
        *,
        start_row: int = 0,
        page_size: int = 100,
        composite: int = 0,
        object_names: Sequence[str] | None = None,
        field_names: Sequence[str] | None = None,
        equality_filter: EqualityFilter | None = None,
        only_view_fields: bool = False,
    ) -> Page[DynamicRecord]:
        """Retrieve and atomically normalize one view-based record page.

        Args:
            view_id: BCIC view identifier.
            start_row: Zero-based first row.
            page_size: Positive requested row count.
            composite: Non-negative composite expansion depth.
            object_names: Optional object-name restriction.
            field_names: Optional returned-field restriction.
            equality_filter: Optional named equality filter.
            only_view_fields: Request only fields configured on the view.

        Returns:
            A typed record page with normalized metadata.

        Raises:
            ValidationError: If options or response data are invalid.
            BCICError: For mapped request failures.
        """
        options = RecordPageOptions(
            view_id=view_id,
            start_row=start_row,
            page_size=page_size,
            composite=composite,
            object_names=tuple(object_names) if object_names is not None else None,
            field_names=tuple(field_names) if field_names is not None else None,
            equality_filter=equality_filter,
            only_view_fields=only_view_fields,
        )
        parameters: dict[str, JSONValue] = {
            "viewId": options.view_id,
            "startRow": options.start_row,
            "rowsPerPage": options.page_size,
            "composite": options.composite,
            "onlyViewFields": options.only_view_fields,
        }
        if options.object_names:
            parameters["objNames"] = ",".join(options.object_names)
        if options.field_names:
            parameters["fieldList"] = ",".join(options.field_names)
        if options.equality_filter:
            parameters["filterName"] = options.equality_filter.name
            parameters["filterValue"] = options.equality_filter.value
        payload = self._execute("getPage", parameters)
        raw_items, total_items, has_more = _normalize_page_payload(payload)
        items = [normalize_record(item) for item in raw_items]
        total_pages = (
            (total_items + options.page_size - 1) // options.page_size
            if total_items is not None
            else None
        )
        if has_more is None:
            has_more = len(items) == options.page_size
        return Page[DynamicRecord](
            items=items,
            metadata=PageMetadata(
                page=(options.start_row // options.page_size) + 1,
                page_size=options.page_size,
                start_row=options.start_row,
                returned_count=len(items),
                has_more=has_more,
                total_items=total_items,
                total_pages=total_pages,
            ),
        )

    def list_all(
        self,
        view_id: str,
        *,
        page_size: int = 100,
        max_pages: int = 100,
        max_items: int = 10_000,
        composite: int = 0,
        object_names: Sequence[str] | None = None,
        field_names: Sequence[str] | None = None,
        equality_filter: EqualityFilter | None = None,
        only_view_fields: bool = False,
    ) -> list[DynamicRecord]:
        """Eagerly retrieve all records within explicit safety limits.

        Args:
            view_id: BCIC view identifier.
            page_size: Positive rows requested per page.
            max_pages: Maximum number of requests.
            max_items: Maximum accumulated records.
            composite: Composite expansion depth.
            object_names: Optional object restriction.
            field_names: Optional field restriction.
            equality_filter: Optional named equality filter.
            only_view_fields: Request only fields configured on the view.

        Returns:
            All records when traversal completes within the safeguards.

        Raises:
            PaginationLimitError: If a page or item limit is reached.
            ValidationError: If pagination stalls or data is malformed.
            BCICError: For mapped request failures.
        """
        if page_size <= 0 or max_pages <= 0 or max_items <= 0:
            raise ValidationError("Pagination limits must be positive")

        def fetch(start_row: int) -> Page[DynamicRecord]:
            return self.get_page(
                view_id,
                start_row=start_row,
                page_size=page_size,
                composite=composite,
                object_names=object_names,
                field_names=field_names,
                equality_filter=equality_filter,
                only_view_fields=only_view_fields,
            )

        return traverse_pages(
            fetch,
            page_size=page_size,
            max_pages=max_pages,
            max_items=max_items,
        )

    def create(
        self,
        object_name: str,
        fields: Mapping[str, JSONValue],
        *,
        use_ids: bool = False,
    ) -> RecordCreationResult:
        """Create a record and return its server-assigned identity.

        Args:
            object_name: BCIC object name.
            fields: Non-empty JSON-compatible field mapping.
            use_ids: Interpret field keys as BCIC identifiers when true.

        Returns:
            The created object's normalized identity.

        Raises:
            ValidationError: If input or response data is invalid.
            BCICError: For mapped request failures.
        """
        if not isinstance(fields, Mapping):
            raise ValidationError("Invalid record fields")
        request = CreateRecordRequest(
            object_name=object_name, fields=dict(fields), use_ids=use_ids
        )
        parameters: dict[str, JSONValue] = {
            "objName": request.object_name,
            "useIds": request.use_ids,
            **request.fields,
        }
        payload = self._execute("createRecord", parameters, http_method="POST")
        if not isinstance(payload, Mapping):
            raise ValidationError("Invalid create record response")
        returned_object = payload.get("objName")
        returned_id = payload.get("id")
        try:
            return RecordCreationResult(
                object_name=validate_identifier(returned_object, "create response"),
                record_id=validate_identifier(
                    str(returned_id) if isinstance(returned_id, int) else returned_id,
                    "create response",
                ),
            )
        except ValidationError as error:
            raise ValidationError("Invalid create record response") from error

    def update(
        self,
        object_name: str,
        record_id: str,
        changes: Mapping[str, JSONValue],
        *,
        use_ids: bool = False,
    ) -> RecordUpdateResult:
        """Update only the supplied fields on one existing record.

        Args:
            object_name: BCIC object name.
            record_id: Existing record identifier.
            changes: Non-empty JSON-compatible changes.
            use_ids: Interpret field keys as BCIC identifiers when true.

        Returns:
            The normalized update status.

        Raises:
            ValidationError: If input or response data is invalid.
            BCICError: For mapped request failures.
        """
        if not isinstance(changes, Mapping):
            raise ValidationError("Invalid record changes")
        request = UpdateRecordRequest(
            object_name=object_name,
            record_id=record_id,
            changes=dict(changes),
            use_ids=use_ids,
        )
        payload = self._execute(
            "updateRecord",
            {
                "objName": request.object_name,
                "id": request.record_id,
                "useIds": request.use_ids,
                **request.changes,
            },
            http_method="POST",
        )
        status, message = _normalize_status(payload, "update")
        return RecordUpdateResult(
            object_name=request.object_name,
            record_id=request.record_id,
            status=status,
            message=message,
        )

    def delete(self, object_name: str, record_id: str) -> RecordDeletionResult:
        """Request deletion of a record.

        Normal Platform records move to the Recycle Bin; behavior for external
        objects remains server-defined.

        Args:
            object_name: BCIC object name.
            record_id: Existing record identifier.

        Returns:
            The normalized deletion status.

        Raises:
            ValidationError: If identity or response data is invalid.
            BCICError: For mapped request failures.
        """
        object_name = validate_identifier(object_name, "object name")
        record_id = validate_identifier(record_id, "record ID")
        payload = self._execute(
            "deleteRecord", {"objName": object_name, "id": record_id}
        )
        status, message = _normalize_status(payload, "delete")
        return RecordDeletionResult(
            object_name=object_name,
            record_id=record_id,
            status=status,
            message=message,
        )


def _join_names(values: Sequence[str], label: str) -> str:
    if isinstance(values, str) or not values:
        raise ValidationError(f"Invalid {label}")
    normalized = [validate_identifier(value, label) for value in values]
    return ",".join(normalized)


def _normalize_page_payload(
    payload: dict[str, JSONValue] | list[JSONValue],
) -> tuple[list[object], int | None, bool | None]:
    if isinstance(payload, list):
        return cast(list[object], payload), None, None
    raw_items = payload.get("records", payload.get("items"))
    if not isinstance(raw_items, list):
        raise ValidationError("Invalid record page response")
    raw_total = payload.get("totalItems")
    total = (
        raw_total
        if isinstance(raw_total, int) and not isinstance(raw_total, bool)
        else None
    )
    raw_has_more = payload.get("hasMore")
    has_more = raw_has_more if isinstance(raw_has_more, bool) else None
    return cast(list[object], raw_items), total, has_more


def _normalize_status(
    payload: dict[str, JSONValue] | list[JSONValue], operation: str
) -> tuple[str, str | None]:
    if not isinstance(payload, Mapping):
        raise APIError(f"Invalid {operation} record response")
    status = payload.get("status")
    if not isinstance(status, str) or not status.strip():
        raise APIError(f"Invalid {operation} record response")
    message_value = payload.get("Msg", payload.get("message"))
    if message_value is not None and not isinstance(message_value, str):
        raise APIError(f"Invalid {operation} record response")
    return status.strip(), message_value
