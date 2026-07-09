"""REST v1 HTTP transport and response parsing boundaries."""

import re
from collections.abc import Mapping
from typing import Literal, Protocol, cast

import httpx
from tenacity import Retrying, retry_if_exception_type, stop_after_attempt, wait_fixed

from bcic.config import OutputFormat
from bcic.exceptions import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from bcic.models.records import JSONValue

HTTPMethod = Literal["GET", "POST"]
JSONMapping = dict[str, JSONValue]
type JSONPayload = JSONMapping | list[JSONValue]
_METHOD_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")


def validate_method_name(method_name: str) -> None:
    """Reject values that could escape the REST v1 method path."""
    if _METHOD_NAME.fullmatch(method_name) is None:
        raise ValidationError("Invalid REST method name")


class AuthenticationStrategy(Protocol):
    """Authentication behavior required by the transport."""

    def request_headers(self) -> dict[str, str]:
        """Return headers for an authenticated request."""


class ResponseParser:
    """Normalize transport responses without exposing raw HTTP objects."""

    def parse(
        self, response: httpx.Response, output_format: OutputFormat
    ) -> JSONPayload:
        """Parse a successful response into a JSON mapping or array."""
        if output_format != "json":
            raise ValidationError(f"Unsupported output format: {output_format}")
        try:
            payload = response.json()
        except (ValueError, UnicodeDecodeError) as error:
            raise APIError("Invalid BCIC response") from error
        if isinstance(payload, dict) and all(isinstance(key, str) for key in payload):
            return cast(JSONMapping, payload)
        if isinstance(payload, list):
            return cast(list[JSONValue], payload)
        else:
            raise APIError("Invalid BCIC response")


class RestTransport:
    """Execute REST v1 method calls through an injectable HTTP client."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
        parser: ResponseParser | None = None,
        max_retries: int = 3,
        retry_wait_seconds: float = 0.5,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._owns_client = client is None
        self._client = client or httpx.Client(timeout=timeout)
        self._parser = parser or ResponseParser()
        self.authentication: AuthenticationStrategy | None = None
        self._closed = False
        self._retryer = Retrying(
            stop=stop_after_attempt(max_retries + 1),
            wait=wait_fixed(retry_wait_seconds),
            retry=retry_if_exception_type((NetworkError, RateLimitError, ServerError)),
            reraise=True,
        )

    def execute(
        self,
        method_name: str,
        parameters: Mapping[str, JSONValue] | None = None,
        *,
        http_method: HTTPMethod = "GET",
        output_format: OutputFormat = "json",
        headers: Mapping[str, str] | None = None,
        authenticate: bool = True,
    ) -> JSONPayload:
        """Execute one validated REST v1 method."""
        if self._closed:
            raise APIError("Client is closed")
        validate_method_name(method_name)
        url = f"{self._base_url}/rest/api/{method_name}"
        request_parameters = dict(parameters or {})
        request_headers = dict(headers or {})
        if authenticate and self.authentication is not None:
            request_headers.update(self.authentication.request_headers())
        return self._retryer(
            self._execute_once,
            url,
            request_parameters,
            http_method,
            output_format,
            request_headers,
        )

    def _execute_once(
        self,
        url: str,
        request_parameters: JSONMapping,
        http_method: HTTPMethod,
        output_format: OutputFormat,
        request_headers: Mapping[str, str],
    ) -> JSONPayload:
        """Perform and map one HTTP attempt."""
        try:
            response = self._send(url, request_parameters, http_method, request_headers)
        except (httpx.TimeoutException, httpx.NetworkError) as error:
            raise NetworkError("BCIC request failed") from error
        self._raise_for_http_status(response.status_code)
        payload = self._parser.parse(response, output_format)
        if isinstance(payload, dict):
            self._raise_for_bcic_status(payload)
        return payload

    def _send(
        self,
        url: str,
        request_parameters: JSONMapping,
        http_method: HTTPMethod,
        request_headers: Mapping[str, str],
    ) -> httpx.Response:
        """Send one HTTP request."""
        if http_method == "GET":
            query_parameters = cast(
                Mapping[str, str | int | float | bool | None],
                request_parameters,
            )
            return self._client.get(
                url, params=query_parameters, headers=request_headers
            )
        if http_method == "POST":
            return self._client.post(
                url, json=request_parameters, headers=request_headers
            )
        raise ValidationError("Unsupported HTTP method")

    @staticmethod
    def _raise_for_http_status(status_code: int) -> None:
        if status_code < 400:
            return
        if status_code == 400:
            raise ValidationError("BCIC request was rejected")
        if status_code == 401:
            raise AuthenticationError("BCIC authentication failed")
        if status_code == 403:
            raise AuthorizationError("BCIC permission denied")
        if status_code == 404:
            raise NotFoundError("BCIC resource not found")
        if status_code == 429:
            raise RateLimitError("BCIC rate limit exceeded")
        if status_code >= 500:
            raise ServerError("BCIC server request failed")
        raise APIError("BCIC API request failed")

    @staticmethod
    def _raise_for_bcic_status(payload: JSONMapping) -> None:
        status = payload.get("status")
        if not isinstance(status, str) or status.lower() in {"ok", "success"}:
            return
        normalized = status.lower()
        if normalized in {"login", "authentication"}:
            raise AuthenticationError("BCIC authentication failed")
        if normalized in {"permission", "authorization", "forbidden"}:
            raise AuthorizationError("BCIC permission denied")
        if normalized in {"validation", "invalid"}:
            raise ValidationError("BCIC request was rejected")
        raise APIError("BCIC API request failed")

    def close(self) -> None:
        """Close owned HTTP resources once and disable further requests."""
        if self._closed:
            return
        self._closed = True
        if self._owns_client:
            self._client.close()
