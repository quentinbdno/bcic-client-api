"""Shared endpoint composition boundary."""

from dataclasses import dataclass
from typing import ClassVar

from bcic.auth import SessionAuth
from bcic.config import ClientConfig
from bcic.transport import ResponseParser, RestTransport


@dataclass(frozen=True, slots=True)
class _AuthenticationDependencies:
    """Configuration available to the future authentication adapter."""

    config: ClientConfig
    strategy: SessionAuth


@dataclass(frozen=True, slots=True)
class _TransportDependencies:
    """Configuration available to the future transport adapter."""

    config: ClientConfig
    transport: RestTransport


@dataclass(frozen=True, slots=True)
class _ParserDependencies:
    """Configuration available to the future response parser."""

    config: ClientConfig
    parser: ResponseParser


@dataclass(frozen=True, slots=True)
class _EndpointContext:
    """Private dependencies shared by all endpoints for one client."""

    config: ClientConfig
    authentication: _AuthenticationDependencies
    transport: _TransportDependencies
    parser: _ParserDependencies


class BaseEndpoint:
    """Base for endpoints composed from shared client dependencies."""

    REST_METHODS: ClassVar[tuple[str, ...]] = ()

    def __init__(self, context: _EndpointContext) -> None:
        self._context = context
