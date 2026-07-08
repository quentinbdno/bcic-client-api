import logging
from collections.abc import Iterator, Mapping

import pytest

from bcic import Client
from bcic.exceptions import ConfigurationError


class FailingEnvironment(Mapping[str, str]):
    def __getitem__(self, key: str) -> str:
        raise AssertionError(f"environment read during import: {key}")

    def __iter__(self) -> Iterator[str]:
        raise AssertionError("environment iterated during import")

    def __len__(self) -> int:
        raise AssertionError("environment sized during import")


def test_client_accepts_explicit_configuration() -> None:
    client = Client(
        base_url="https://example.bcic.test/",
        username="integration-user",
        password="secret-value",
        timeout=12.5,
        max_retries=4,
        retry_wait_seconds=0.25,
        output_format="xml",
    )

    assert client.config.base_url == "https://example.bcic.test"
    assert client.config.username == "integration-user"
    assert client.config.password.get_secret_value() == "secret-value"
    assert client.config.timeout == 12.5
    assert client.config.max_retries == 4
    assert client.config.retry_wait_seconds == 0.25
    assert client.config.output_format == "xml"
    assert "secret-value" not in repr(client.config)


def test_client_uses_safe_defaults() -> None:
    client = Client(
        base_url="https://example.bcic.test",
        username="integration-user",
        password="secret-value",
    )

    assert client.config.timeout == 30.0
    assert client.config.max_retries == 3
    assert client.config.retry_wait_seconds == 0.5
    assert client.config.output_format == "json"


def test_client_from_env_supports_explicit_precedence() -> None:
    environment = {
        "BCIC_BASE_URL": "https://environment.bcic.test/",
        "BCIC_USERNAME": "environment-user",
        "BCIC_PASSWORD": "environment-secret",
        "BCIC_TIMEOUT": "20",
        "BCIC_MAX_RETRIES": "2",
        "BCIC_RETRY_WAIT_SECONDS": "1.5",
        "BCIC_OUTPUT_FORMAT": "xml",
    }

    client = Client.from_env(
        environment,
        base_url="https://explicit.bcic.test",
        username="explicit-user",
        password="explicit-secret",
        timeout=10,
    )

    assert client.config.base_url == "https://explicit.bcic.test"
    assert client.config.username == "explicit-user"
    assert client.config.password.get_secret_value() == "explicit-secret"
    assert client.config.timeout == 10
    assert client.config.max_retries == 2
    assert client.config.output_format == "xml"


@pytest.mark.parametrize(
    ("overrides", "secret"),
    [
        ({"base_url": "not-a-url"}, "not-a-url"),
        ({"username": ""}, "secret-value"),
        ({"password": ""}, "integration-user"),
        ({"timeout": 0}, "secret-value"),
        ({"max_retries": -1}, "secret-value"),
        ({"retry_wait_seconds": -1}, "secret-value"),
        ({"output_format": "yaml"}, "secret-value"),
    ],
)
def test_invalid_configuration_is_sanitized(
    overrides: dict[str, object], secret: str
) -> None:
    values: dict[str, object] = {
        "base_url": "https://example.bcic.test",
        "username": "integration-user",
        "password": "secret-value",
    }
    values.update(overrides)

    with pytest.raises(ConfigurationError) as error:
        Client(**values)  # type: ignore[arg-type]

    assert str(error.value) == "Invalid BCIC client configuration"
    assert secret not in str(error.value)


def test_from_env_reports_missing_configuration_without_values() -> None:
    with pytest.raises(ConfigurationError) as error:
        Client.from_env({})

    assert str(error.value) == "Invalid BCIC client configuration"


def test_configuration_does_not_emit_logs(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        Client(
            base_url="https://example.bcic.test",
            username="integration-user",
            password="secret-value",
        )

    assert caplog.records == []
