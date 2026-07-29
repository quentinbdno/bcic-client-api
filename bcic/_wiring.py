"""Private version-aware composition for client internals."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

import httpx

from bcic.config import ApiVersion
from bcic.exceptions import ValidationError

if TYPE_CHECKING:
    from bcic.transport import ResponseParser, RestTransport


class RestAdapter(Protocol):
    """Version-specific behavior required by the REST transport."""

    def build_url(self, base_url: str, method_name: str) -> str:
        """Build a request URL for one BCIC method."""

    def request_headers(self, method_name: str) -> Mapping[str, str]:
        """Return version-specific request headers."""


@dataclass(frozen=True, slots=True)
class RestV1Adapter:
    """REST v1 method adapter preserving the existing request path."""

    def build_url(self, base_url: str, method_name: str) -> str:
        """Build a REST v1 method URL."""
        return f"{base_url}/rest/api/{method_name}"

    def request_headers(self, method_name: str) -> Mapping[str, str]:
        """Return REST v1 request headers."""
        return {}


@dataclass(frozen=True, slots=True)
class RestV2Adapter:
    """REST v2 method adapter distinct from the v1 request path."""

    def build_url(self, base_url: str, method_name: str) -> str:
        """Build a REST v2 method URL."""
        if method_name in {"login", "logout"}:
            return f"{base_url}/userResource/{method_name}"
        return f"{base_url}/customMethod/{method_name}"

    def request_headers(self, method_name: str) -> Mapping[str, str]:
        """Return REST v2 request headers."""
        return {"Accept-Version": "latest"}


@dataclass(frozen=True, slots=True)
class AdapterSet:
    """Resolved internal adapters for one API version."""

    api_version: ApiVersion
    transport: RestAdapter

    def create_transport(
        self,
        base_url: str,
        *,
        timeout: float = 30.0,
        client: httpx.Client | None = None,
        parser: ResponseParser | None = None,
        max_retries: int = 3,
        retry_wait_seconds: float = 0.5,
    ) -> RestTransport:
        """Create a transport bound to this adapter set."""
        from bcic.transport import RestTransport

        return RestTransport(
            base_url,
            timeout=timeout,
            client=client,
            parser=parser,
            max_retries=max_retries,
            retry_wait_seconds=retry_wait_seconds,
            adapter=self.transport,
        )


def resolve_adapter_set(api_version: ApiVersion | str) -> AdapterSet:
    """Resolve private client adapters from a validated API version."""
    if api_version == "v1":
        return AdapterSet(api_version="v1", transport=RestV1Adapter())
    if api_version == "v2":
        return AdapterSet(api_version="v2", transport=RestV2Adapter())
    raise ValidationError("Unsupported API version")
