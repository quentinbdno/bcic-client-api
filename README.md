# BCIC Client API

Python client SDK for the BCIC API.

## Overview

`bcic-client-api` provides a typed Python interface for interacting with BCIC through:

- session authentication
- API key authentication
- record operations
- user, role, and permission queries
- binary and lower-level REST method access

The public entry point is `bcic.Client`.

## Requirements

- Python 3.12+
- A reachable BCIC tenant base URL

## Installation

```bash
pip install bcic-client-api
```

## Quick Start

### Session authentication

```python
from bcic import Client

client = Client(
    base_url="https://your-bcic-tenant.example.com",
    username="your-username",
    password="your-password",
)

client.authenticate()
try:
    records = client.records.list_all("YourViewId")
    print(records)
finally:
    client.logout()
    client.close()
```

### API key authentication

```python
from bcic import Client

client = Client(
    base_url="https://your-bcic-tenant.example.com",
    auth_mode="api_key",
    api_key="your-api-key",
)

result = client.methods.execute("getRoles")
print(result)
client.close()
```

### Context manager

```python
from bcic import Client

with Client(
    base_url="https://your-bcic-tenant.example.com",
    username="your-username",
    password="your-password",
) as client:
    client.authenticate()
    user_roles = client.users.list_roles()
    print(user_roles)
```

## Environment Variables

`Client.from_env()` can build a configured client from environment values.

Supported variables:

- `BCIC_BASE_URL`
- `BCIC_USERNAME`
- `BCIC_PASSWORD`
- `BCIC_AUTH_MODE`
- `BCIC_API_KEY`
- `BCIC_API_KEY_HEADER`
- `BCIC_API_VERSION`
- `BCIC_TIMEOUT`
- `BCIC_MAX_RETRIES`
- `BCIC_RETRY_WAIT_SECONDS`
- `BCIC_OUTPUT_FORMAT`

Example:

```python
from bcic import Client

client = Client.from_env()
```

## Public API

### `Client`

The client exposes these domain endpoints:

- `client.records`
- `client.users`
- `client.binary`
- `client.methods`

Common lifecycle methods:

- `client.authenticate()`
- `client.logout()`
- `client.close()`

### Records

```python
record = client.records.get("ObjectName", "RecordId")
page = client.records.get_page("ViewId", page_size=100)
items = client.records.list_all("ViewId")
created = client.records.create("ObjectName", {"Field1": "value"})
updated = client.records.update("ObjectName", "RecordId", {"Field1": "new value"})
deleted = client.records.delete("ObjectName", "RecordId")
```

### Users

```python
roles = client.users.list_roles()
role = client.users.get_role("RoleId")
permissions = client.users.get_permissions_by_role("RoleId", "object")
user_permissions = client.users.get_permissions_by_user("UserId", "menu", application_id="AppId")
```

### Methods

Use `client.methods.execute()` for controlled lower-level REST method access when a domain-specific helper is not available.

```python
payload = client.methods.execute("getRoles")
```

## Configuration

The client validates configuration at construction time and raises `ConfigurationError` for invalid settings.

Supported authentication modes:

- `session`
- `api_key`

Default values:

- `auth_mode="session"`
- `api_key_header="Api-Key"`
- `api_version="v1"`
- `timeout=30.0`
- `max_retries=3`
- `retry_wait_seconds=0.5`
- `output_format="json"`

## Exceptions

The SDK raises a shared base exception type, `bcic.exceptions.BCICError`, with more specific subclasses such as:

- `ConfigurationError`
- `AuthenticationError`
- `AuthorizationError`
- `ValidationError`
- `APIError`
- `RateLimitError`
- `NotFoundError`
- `ServerError`
- `NetworkError`

## Development

```bash
poetry install
poetry run pytest
poetry run ruff check .
poetry run mypy bcic
```

## Packaging

Build artifacts:

```bash
poetry build
```

Validate the distribution before publishing:

```bash
twine check dist/*
```

## Publishing

Recommended release flow:

1. Bump the version in `pyproject.toml`.
2. Run the test suite.
3. Build the package.
4. Upload to TestPyPI first.
5. Verify installation from TestPyPI.
6. Upload to PyPI.

## License

MIT
