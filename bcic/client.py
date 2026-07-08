"""BCIC client entry point."""

import os
from collections.abc import Mapping

from pydantic import SecretStr, ValidationError

from bcic.config import ClientConfig, OutputFormat
from bcic.endpoints import (
    BinaryEndpoint,
    MethodsEndpoint,
    RecordsEndpoint,
    UsersEndpoint,
)
from bcic.endpoints.base import (
    _AuthenticationDependencies,
    _EndpointContext,
    _ParserDependencies,
    _TransportDependencies,
)
from bcic.exceptions import ConfigurationError


class Client:
    """Configured client for interacting with BCIC.

    Construction validates settings without performing authentication or any
    network request.
    """

    def __init__(
        self,
        *,
        base_url: str,
        username: str,
        password: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_wait_seconds: float = 0.5,
        output_format: OutputFormat = "json",
    ) -> None:
        """Create a client from explicit validated configuration values."""
        try:
            self._config = ClientConfig(
                base_url=base_url,
                username=username,
                password=SecretStr(password),
                timeout=timeout,
                max_retries=max_retries,
                retry_wait_seconds=retry_wait_seconds,
                output_format=output_format,
            )
        except ValidationError as error:
            raise ConfigurationError("Invalid BCIC client configuration") from error
        context = _EndpointContext(
            config=self._config,
            authentication=_AuthenticationDependencies(self._config),
            transport=_TransportDependencies(self._config),
            parser=_ParserDependencies(self._config),
        )
        self._records = RecordsEndpoint(context)
        self._users = UsersEndpoint(context)
        self._binary = BinaryEndpoint(context)
        self._methods = MethodsEndpoint(context)

    @property
    def config(self) -> ClientConfig:
        """Return the client's immutable validated configuration."""
        return self._config

    @property
    def records(self) -> RecordsEndpoint:
        """Return the stable record-domain endpoint."""
        return self._records

    @property
    def users(self) -> UsersEndpoint:
        """Return the stable user-domain endpoint."""
        return self._users

    @property
    def binary(self) -> BinaryEndpoint:
        """Return the stable binary-domain endpoint."""
        return self._binary

    @property
    def methods(self) -> MethodsEndpoint:
        """Return the lower-level generic-method endpoint."""
        return self._methods

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: float | str | None = None,
        max_retries: int | str | None = None,
        retry_wait_seconds: float | str | None = None,
        output_format: OutputFormat | None = None,
    ) -> "Client":
        """Create a client from BCIC environment variables and explicit overrides."""
        source = os.environ if environ is None else environ
        values = {
            "base_url": (
                base_url if base_url is not None else source.get("BCIC_BASE_URL")
            ),
            "username": (
                username if username is not None else source.get("BCIC_USERNAME")
            ),
            "password": (
                password if password is not None else source.get("BCIC_PASSWORD")
            ),
            "timeout": (
                timeout if timeout is not None else source.get("BCIC_TIMEOUT", 30.0)
            ),
            "max_retries": (
                max_retries
                if max_retries is not None
                else source.get("BCIC_MAX_RETRIES", 3)
            ),
            "retry_wait_seconds": (
                retry_wait_seconds
                if retry_wait_seconds is not None
                else source.get("BCIC_RETRY_WAIT_SECONDS", 0.5)
            ),
            "output_format": (
                output_format
                if output_format is not None
                else source.get("BCIC_OUTPUT_FORMAT", "json")
            ),
        }
        try:
            config = ClientConfig.model_validate(values)
        except ValidationError as error:
            raise ConfigurationError("Invalid BCIC client configuration") from error

        return cls(
            base_url=config.base_url,
            username=config.username,
            password=config.password.get_secret_value(),
            timeout=config.timeout,
            max_retries=config.max_retries,
            retry_wait_seconds=config.retry_wait_seconds,
            output_format=config.output_format,
        )
