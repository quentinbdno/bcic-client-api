"""Validated BCIC client configuration."""

import math
from typing import Literal
from urllib.parse import urlsplit

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)

OutputFormat = Literal["json", "xml"]
AuthMode = Literal["session", "api_key"]


class ClientConfig(BaseModel):
    """Immutable validated settings shared by BCIC client components."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    base_url: str
    username: str | None = Field(default=None)
    password: SecretStr | None = Field(default=None)
    auth_mode: AuthMode = "session"
    api_key: SecretStr | None = Field(default=None)
    api_key_header: str = Field(default="Api-Key", min_length=1)
    timeout: float = Field(default=30.0, gt=0)
    max_retries: int = Field(default=3, ge=0)
    retry_wait_seconds: float = Field(default=0.5, ge=0)
    output_format: OutputFormat = "json"

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        """Validate and normalize an HTTP(S) BCIC base URL."""
        parsed = urlsplit(value)
        try:
            parsed.port
        except ValueError as error:
            raise ValueError("base URL must include a valid authority") from error
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.hostname is None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or any(character.isspace() for character in parsed.netloc)
        ):
            raise ValueError("base URL must be an HTTP(S) URL without credentials")
        return value.rstrip("/")

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str | None) -> str | None:
        """Reject credentials that are present but semantically blank."""
        if value is None:
            return value
        if not value.strip():
            raise ValueError("username must not be blank")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr | None) -> SecretStr | None:
        """Reject credentials that are present but semantically blank."""
        if value is None:
            return value
        if not value.get_secret_value().strip():
            raise ValueError("password must not be blank")
        return value

    @field_validator("auth_mode", mode="before")
    @classmethod
    def normalize_auth_mode(cls, value: object) -> object:
        """Normalize auth mode values loaded from environment variables."""
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: SecretStr | None) -> SecretStr | None:
        """Reject API keys that are present but semantically blank."""
        if value is None:
            return value
        if not value.get_secret_value().strip():
            raise ValueError("api_key must not be blank")
        return value

    @field_validator("api_key_header")
    @classmethod
    def validate_api_key_header(cls, value: str) -> str:
        """Reject blank API key header names."""
        if not value.strip():
            raise ValueError("api_key_header must not be blank")
        return value

    @field_validator("timeout", "retry_wait_seconds")
    @classmethod
    def validate_finite_duration(cls, value: float) -> float:
        """Reject non-finite durations that cannot be used safely."""
        if not math.isfinite(value):
            raise ValueError("duration must be finite")
        return value

    @field_validator("max_retries", mode="before")
    @classmethod
    def reject_boolean_retry_count(cls, value: object) -> object:
        """Reject bools before Python treats them as integers."""
        if isinstance(value, bool):
            raise ValueError("max retries must be an integer")
        return value

    @model_validator(mode="after")
    def validate_auth_mode_requirements(self) -> "ClientConfig":
        """Enforce auth-mode-specific configuration requirements."""
        if self.auth_mode == "session":
            if self.username is None:
                raise ValueError("username is required for session auth")
            if self.password is None:
                raise ValueError("password is required for session auth")
            return self
        if self.auth_mode == "api_key":
            if self.api_key is None:
                raise ValueError("api_key is required for api_key auth")
            return self
        raise ValueError("Unsupported authentication mode")
