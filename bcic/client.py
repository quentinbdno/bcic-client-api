"""BCIC client entry point."""

import os
from collections.abc import Mapping

import httpx
from pydantic import SecretStr, ValidationError

from bcic.auth import ApiKeyAuth, AuthStrategy, SessionAuth
from bcic.config import AuthMode, ClientConfig, OutputFormat
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
from bcic.transport import ResponseParser, RestTransport


def _has_text(value: str | None) -> bool:
    """Return whether a string value is present and non-blank."""
    return value is not None and bool(value.strip())


class Client:
    """Configured client for interacting with BCIC.

    Construction validates settings without performing authentication or any
    network request.
    """

    def __init__(
        self,
        *,
        base_url: str,
        username: str | None = None,
        password: str | None = None,
        auth_mode: AuthMode = "session",
        api_key: str | None = None,
        api_key_header: str = "Api-Key",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_wait_seconds: float = 0.5,
        output_format: OutputFormat = "json",
        http_client: httpx.Client | None = None,
    ) -> None:
        """Create a client from explicit validated configuration values.

        Args:
            base_url: BCIC tenant base URL without credentials.
            username: Login name used when a session is established.
            password: Login secret retained as a protected configuration value.
            auth_mode: Authentication mode; defaults to session auth.
            api_key: API key used when ``auth_mode="api_key"``.
            api_key_header: Header name used for API-key authentication.
            timeout: HTTP timeout in seconds.
            max_retries: Retry attempts after the initial request.
            retry_wait_seconds: Fixed delay between retryable attempts.
            output_format: Configured response format; domain APIs require JSON.
            http_client: Optional injected synchronous HTTP client.

        Raises:
            ConfigurationError: If any configuration value is invalid.
        """
        try:
            self._config = ClientConfig(
                base_url=base_url,
                username=username,
                password=SecretStr(password) if password is not None else None,
                auth_mode=auth_mode,
                api_key=SecretStr(api_key) if api_key is not None else None,
                api_key_header=api_key_header,
                timeout=timeout,
                max_retries=max_retries,
                retry_wait_seconds=retry_wait_seconds,
                output_format=output_format,
            )
        except ValidationError as error:
            raise ConfigurationError("Invalid BCIC client configuration") from error
        parser = ResponseParser()
        transport = RestTransport(
            self._config.base_url,
            timeout=self._config.timeout,
            client=http_client,
            parser=parser,
            max_retries=self._config.max_retries,
            retry_wait_seconds=self._config.retry_wait_seconds,
        )
        self._authentication: AuthStrategy
        if self._config.auth_mode == "api_key":
            self._authentication = ApiKeyAuth(self._config)
        else:
            self._authentication = SessionAuth(self._config, transport)
        self._transport = transport
        transport.authentication = self._authentication
        context = _EndpointContext(
            config=self._config,
            authentication=_AuthenticationDependencies(
                self._config, self._authentication
            ),
            transport=_TransportDependencies(self._config, transport),
            parser=_ParserDependencies(self._config, parser),
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

    def authenticate(self) -> None:
        """Establish and retain a private BCIC REST v1 session.

        Raises:
            AuthenticationError: If BCIC does not establish a valid session.
            BCICError: For another mapped transport or API failure.
        """
        self._authentication.authenticate()

    def logout(self) -> None:
        """Terminate the active BCIC session, if one exists.

        The operation is idempotent. Mapped SDK exceptions may be raised when
        remote termination of an active session fails.
        """
        self._authentication.logout()

    def close(self) -> None:
        """Release owned HTTP resources; repeated calls are safe."""
        self._transport.close()

    def __enter__(self) -> "Client":
        """Enter a client context."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Close the client without suppressing a body exception."""
        self.close()

    @classmethod
    def from_env(
        cls,
        environ: Mapping[str, str] | None = None,
        *,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        auth_mode: AuthMode | None = None,
        api_key: str | None = None,
        api_key_header: str | None = None,
        timeout: float | str | None = None,
        max_retries: int | str | None = None,
        retry_wait_seconds: float | str | None = None,
        output_format: OutputFormat | None = None,
    ) -> "Client":
        """Create a client from BCIC environment variables and overrides.

        Args:
            environ: Optional environment mapping; defaults to ``os.environ``.
            base_url: Explicit override for ``BCIC_BASE_URL``.
            username: Explicit override for ``BCIC_USERNAME``.
            password: Explicit override for ``BCIC_PASSWORD``.
            auth_mode: Explicit override for ``BCIC_AUTH_MODE``.
            api_key: Explicit override for ``BCIC_API_KEY``.
            api_key_header: Explicit override for ``BCIC_API_KEY_HEADER``.
            timeout: Explicit override for ``BCIC_TIMEOUT``.
            max_retries: Explicit override for ``BCIC_MAX_RETRIES``.
            retry_wait_seconds: Override for ``BCIC_RETRY_WAIT_SECONDS``.
            output_format: Explicit override for ``BCIC_OUTPUT_FORMAT``.

        Returns:
            A validated client that has not performed network I/O.

        Raises:
            ConfigurationError: If required values are absent or invalid.
        """
        source = os.environ if environ is None else environ
        resolved_username = (
            username if username is not None else source.get("BCIC_USERNAME")
        )
        resolved_password = (
            password if password is not None else source.get("BCIC_PASSWORD")
        )
        resolved_api_key = (
            api_key if api_key is not None else source.get("BCIC_API_KEY")
        )

        has_username = _has_text(resolved_username)
        has_password = _has_text(resolved_password)
        has_api_key = _has_text(resolved_api_key)

        selected_auth_mode: AuthMode | str
        if auth_mode is not None:
            selected_auth_mode = auth_mode
        else:
            env_auth_mode = source.get("BCIC_AUTH_MODE")
            if _has_text(env_auth_mode):
                selected_auth_mode = env_auth_mode  # normalized by ClientConfig
            elif has_api_key:
                selected_auth_mode = "api_key"
            elif has_username and has_password:
                selected_auth_mode = "session"
            else:
                raise ConfigurationError("authentication data missing")

        normalized_mode = (
            selected_auth_mode.strip().lower()
            if isinstance(selected_auth_mode, str)
            else selected_auth_mode
        )
        if normalized_mode == "api_key" and not has_api_key:
            raise ConfigurationError("authentication data missing")
        if normalized_mode == "session" and not (has_username and has_password):
            raise ConfigurationError("authentication data missing")

        values = {
            "base_url": (
                base_url if base_url is not None else source.get("BCIC_BASE_URL")
            ),
            "username": resolved_username,
            "password": resolved_password,
            "auth_mode": selected_auth_mode,
            "api_key": resolved_api_key,
            "api_key_header": (
                api_key_header
                if api_key_header is not None
                else source.get("BCIC_API_KEY_HEADER", "Api-Key")
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
            password=(
                config.password.get_secret_value()
                if config.password is not None
                else None
            ),
            auth_mode=config.auth_mode,
            api_key=(
                config.api_key.get_secret_value()
                if config.api_key is not None
                else None
            ),
            api_key_header=config.api_key_header,
            timeout=config.timeout,
            max_retries=config.max_retries,
            retry_wait_seconds=config.retry_wait_seconds,
            output_format=config.output_format,
        )
