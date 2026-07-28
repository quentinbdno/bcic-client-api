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


def test_config_accepts_api_key_mode_without_username_password() -> None:
    configured = config(
        auth_mode="api_key",
        username=None,
        password=None,
        api_key="fixture-api-key",
    )

    assert configured.auth_mode == "api_key"
    assert configured.api_key is not None
    assert configured.api_key.get_secret_value() == "fixture-api-key"


@pytest.mark.parametrize(
    "values",
    [
        {"username": None},
        {"password": None},
        {"username": "   "},
        {"password": "   "},
    ],
)
def test_config_rejects_incomplete_session_auth(values: dict[str, object]) -> None:
    with pytest.raises(PydanticValidationError):
        config(**values)


@pytest.mark.parametrize(
    "values",
    [
        {"auth_mode": "api_key", "username": None, "password": None},
        {
            "auth_mode": "api_key",
            "username": None,
            "password": None,
            "api_key": "",
        },
        {
            "auth_mode": "api_key",
            "username": None,
            "password": None,
            "api_key": "   ",
        },
    ],
)
def test_config_rejects_missing_or_blank_api_key(values: dict[str, object]) -> None:
    with pytest.raises(PydanticValidationError):
        config(**values)


def test_config_normalizes_auth_mode_loaded_from_environment() -> None:
    configured = config(
        auth_mode=" API_KEY ",
        username=None,
        password=None,
        api_key="k",
    )
    assert configured.auth_mode == "api_key"


def test_config_accepts_api_version() -> None:
    configured = config(api_version=" v2 ")

    assert configured.api_version == "v2"
