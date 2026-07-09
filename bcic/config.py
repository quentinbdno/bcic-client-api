"""Validated BCIC client configuration."""

import math
from typing import Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

OutputFormat = Literal["json", "xml"]


class ClientConfig(BaseModel):
    """Immutable validated settings shared by BCIC client components."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    base_url: str
    username: str = Field(min_length=1)
    password: SecretStr = Field(min_length=1)
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
    def validate_username(cls, value: str) -> str:
        """Reject credentials that are present but semantically blank."""
        if not value.strip():
            raise ValueError("username must not be blank")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: SecretStr) -> SecretStr:
        """Reject credentials that are present but semantically blank."""
        if not value.get_secret_value().strip():
            raise ValueError("password must not be blank")
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
