"""Validated BCIC client configuration."""

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
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.netloc
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("base URL must be an HTTP(S) URL without credentials")
        return value.rstrip("/")
