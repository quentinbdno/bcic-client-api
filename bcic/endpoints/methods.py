"""Generic REST-method endpoint foundation."""

from collections.abc import Mapping
from typing import cast

from bcic.config import OutputFormat
from bcic.endpoints.base import BaseEndpoint
from bcic.exceptions import ValidationError
from bcic.models.records import JSONValue
from bcic.transport import HTTPMethod, JSONMapping, validate_method_name


def _is_json_value(value: object) -> bool:
    if value is None or isinstance(value, str | int | float | bool):
        return True
    if isinstance(value, list):
        return all(_is_json_value(item) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and _is_json_value(item) for key, item in value.items()
        )
    return False


class MethodsEndpoint(BaseEndpoint):
    """Lower-level entry point for controlled methods introduced by Epic 2."""

    def execute(
        self,
        method_name: str,
        parameters: Mapping[str, JSONValue] | None = None,
        *,
        http_method: HTTPMethod = "GET",
        output_format: OutputFormat | None = None,
    ) -> JSONMapping:
        """Execute a lower-level method; prefer a domain endpoint when available."""
        validate_method_name(method_name)
        if http_method not in {"GET", "POST"}:
            raise ValidationError("Unsupported HTTP method")
        resolved_format = output_format or self._context.config.output_format
        if resolved_format not in {"json", "xml"}:
            raise ValidationError("Unsupported output format")
        if parameters is not None and (
            not isinstance(parameters, Mapping)
            or not all(
                isinstance(key, str) and _is_json_value(value)
                for key, value in parameters.items()
            )
        ):
            raise ValidationError("Invalid REST method parameters")
        request_parameters = cast(dict[str, JSONValue], dict(parameters or {}))
        request_parameters["output"] = resolved_format
        return self._context.transport.transport.execute(
            method_name,
            request_parameters,
            http_method=http_method,
            output_format=resolved_format,
        )
