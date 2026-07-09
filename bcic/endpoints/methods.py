"""Generic REST-method endpoint foundation."""

from collections.abc import Mapping
from typing import cast

from bcic.config import OutputFormat
from bcic.endpoints.base import BaseEndpoint
from bcic.exceptions import APIError, ValidationError
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
        """Execute a lower-level method; prefer a domain endpoint when available.

        Args:
            method_name: Safe REST v1 method name, not a URL or path.
            parameters: Optional JSON-compatible request mapping.
            http_method: ``GET`` or ``POST``.
            output_format: Optional configured parser format override.

        Returns:
            A parsed JSON object.

        Raises:
            ValidationError: If method options or parameters are invalid.
            APIError: If a successful response is not a JSON object.
            BCICError: For mapped request failures.
        """
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
        result = self._context.transport.transport.execute(
            method_name,
            request_parameters,
            http_method=http_method,
            output_format=resolved_format,
        )
        if not isinstance(result, dict):
            raise APIError("Invalid BCIC response")
        return result
