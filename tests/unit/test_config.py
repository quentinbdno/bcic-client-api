import math

import pytest
from pydantic import ValidationError as PydanticValidationError

from bcic.config import ClientConfig


def config(**overrides: object) -> ClientConfig:
    values: dict[str, object] = {
        "base_url": "https://sdk-fixture.example.test",
        "username": "fixture-user",
        "password": "fixture-password",
    }
    values.update(overrides)
    return ClientConfig.model_validate(values)


@pytest.mark.parametrize(
    "base_url",
    [
        "https://",
        "https://:443",
        "https://example.test:invalid",
        "https://example.test:99999",
        "https://exa mple.test",
    ],
)
def test_config_rejects_malformed_base_url_authorities(base_url: str) -> None:
    with pytest.raises(PydanticValidationError):
        config(base_url=base_url)


@pytest.mark.parametrize(
    "field",
    ["username", "password"],
)
def test_config_rejects_blank_credentials(field: str) -> None:
    with pytest.raises(PydanticValidationError):
        config(**{field: " \t "})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("timeout", math.inf),
        ("timeout", math.nan),
        ("retry_wait_seconds", math.inf),
        ("retry_wait_seconds", math.nan),
    ],
)
def test_config_rejects_non_finite_durations(field: str, value: float) -> None:
    with pytest.raises(PydanticValidationError):
        config(**{field: value})


def test_config_rejects_boolean_retry_count() -> None:
    with pytest.raises(PydanticValidationError):
        config(max_retries=True)
