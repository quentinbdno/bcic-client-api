"""Safe bounded binary retrieval and upload operations."""

import base64
import binascii
from collections.abc import Mapping

from bcic.endpoints.base import BaseEndpoint
from bcic.exceptions import APIError, ValidationError
from bcic.models.binary import BinaryData, BinaryMetadata, BinaryUploadResult
from bcic.models.records import JSONValue, validate_identifier


class BinaryEndpoint(BaseEndpoint):
    """Entry point for payload-safe buffered binary operations."""

    REST_METHODS = ("getBinaryData", "setBinaryData")
    DEFAULT_MAX_BYTES = 10_485_760

    def get(
        self,
        object_name: str,
        record_id: str,
        field_name: str,
        *,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> BinaryData:
        """Retrieve and strictly decode one bounded attachment."""
        object_name, record_id, field_name = self._validated_identity(
            object_name, record_id, field_name
        )
        max_bytes = self._validate_limit(max_bytes)
        payload = self._context.transport.transport.execute(
            "getBinaryData",
            {
                "objName": object_name,
                "id": record_id,
                "fieldName": field_name,
                "output": self._context.config.output_format,
            },
            output_format=self._context.config.output_format,
        )
        if not isinstance(payload, Mapping) or set(payload) != {field_name}:
            raise ValidationError("Invalid binary response")
        envelope = payload[field_name]
        if not isinstance(envelope, Mapping):
            raise ValidationError("Invalid binary response")
        file_name = self._response_text(envelope.get("fileName"))
        content_type = self._response_text(envelope.get("contentType"))
        encoded = envelope.get("fileData")
        if not isinstance(encoded, str) or not encoded:
            raise ValidationError("Invalid binary response")
        if len(encoded) > ((max_bytes + 2) // 3) * 4:
            raise APIError("Binary content exceeds configured limit")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValidationError("Invalid binary response") from error
        if not content:
            raise ValidationError("Invalid binary response")
        if len(content) > max_bytes:
            raise APIError("Binary content exceeds configured limit")
        return BinaryData(
            content=content,
            metadata=BinaryMetadata(
                object_name=object_name,
                record_id=record_id,
                field_name=field_name,
                file_name=file_name,
                content_type=content_type,
                size=len(content),
            ),
        )

    def set(
        self,
        object_name: str,
        record_id: str,
        field_name: str,
        content: bytes | bytearray | memoryview,
        *,
        file_name: str,
        content_type: str,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> BinaryUploadResult:
        """Upload one validated buffered attachment using Base64 JSON."""
        object_name, record_id, field_name = self._validated_identity(
            object_name, record_id, field_name
        )
        file_name = validate_identifier(file_name, "file name")
        content_type = validate_identifier(content_type, "content type")
        max_bytes = self._validate_limit(max_bytes)
        if isinstance(content, memoryview):
            if not content.readonly:
                raise ValidationError("Invalid binary content")
            raw_content = content.tobytes()
        elif isinstance(content, bytes | bytearray):
            raw_content = bytes(content)
        else:
            raise ValidationError("Invalid binary content")
        if not raw_content:
            raise ValidationError("Invalid binary content")
        if len(raw_content) > max_bytes:
            raise ValidationError("Binary content exceeds configured limit")
        payload = self._context.transport.transport.execute(
            "setBinaryData",
            {
                "objName": object_name,
                "id": record_id,
                "fieldName": field_name,
                "value": base64.b64encode(raw_content).decode("ascii"),
                "contentType": content_type,
                "fileName": file_name,
                "output": self._context.config.output_format,
            },
            http_method="POST",
            output_format=self._context.config.output_format,
        )
        if not isinstance(payload, Mapping):
            raise ValidationError("Invalid binary upload response")
        status = payload.get("status")
        message = payload.get("message")
        if (
            not isinstance(status, str)
            or not status.strip()
            or (message is not None and not isinstance(message, str))
        ):
            raise ValidationError("Invalid binary upload response")
        return BinaryUploadResult(
            object_name=object_name,
            record_id=record_id,
            field_name=field_name,
            status=status.strip(),
            message=message.strip() if isinstance(message, str) else None,
        )

    @staticmethod
    def _validated_identity(
        object_name: str, record_id: str, field_name: str
    ) -> tuple[str, str, str]:
        return (
            validate_identifier(object_name, "object name"),
            validate_identifier(record_id, "record ID"),
            validate_identifier(field_name, "field name"),
        )

    @staticmethod
    def _validate_limit(max_bytes: int) -> int:
        if (
            not isinstance(max_bytes, int)
            or isinstance(max_bytes, bool)
            or max_bytes <= 0
        ):
            raise ValidationError("Invalid binary size limit")
        return max_bytes

    @staticmethod
    def _response_text(value: JSONValue | None) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Invalid binary response")
        return value.strip()
