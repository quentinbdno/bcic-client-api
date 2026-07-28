# Authentication and Lifecycle

The SDK supports two authentication modes:

- `session` (default): authenticates with `username` and `password`, then reuses
    the returned BCIC `sessionId`.
- `api_key`: attaches a configured API key header to each request and does not
    call `login`/`logout` endpoints.

When `BCIC_AUTH_MODE` is not provided, the SDK auto-selects authentication:

- If `BCIC_API_KEY` is present, mode becomes `api_key`.
- Otherwise, if both `BCIC_USERNAME` and `BCIC_PASSWORD` are present, mode
    becomes `session`.
- If neither set is present, the client raises
    `ConfigurationError("authentication data missing")`.

## Environment configuration

`Client.from_env()` reads:

- `BCIC_BASE_URL` (required)
- `BCIC_AUTH_MODE` (`session` by default)
- `BCIC_USERNAME` and `BCIC_PASSWORD` (required for `session` mode)
- `BCIC_API_KEY` (required for `api_key` mode)
- `BCIC_API_KEY_HEADER` (optional, default `Api-Key`)
- `BCIC_API_VERSION` (optional, default `v1`)
- `BCIC_TIMEOUT` (default `30`)
- `BCIC_MAX_RETRIES` (default `3`)
- `BCIC_RETRY_WAIT_SECONDS` (default `0.5`)
- `BCIC_OUTPUT_FORMAT` (default `json`)

```python
from bcic import Client

with Client.from_env() as client:
    roles = client.users.list_roles()
```

API-key mode:

```python
from bcic import Client

with Client(
    base_url="https://example.bcic.test",
    auth_mode="api_key",
    api_key="YOUR_API_KEY",
) as client:
    roles = client.users.list_roles()
```

Explicit keyword arguments to `from_env()` take precedence over environment
values. Never commit credentials or place them in URLs.

`BCIC_API_VERSION` selects the transport contract used by the client. The
current SDK ships with a v1 transport as the default and a separate v2 branch
for version-aware routing.

## Sessions and cleanup

Client construction is offline. In `session` mode, call
`client.authenticate()` for eager login or let the first operation authenticate
lazily. Session IDs stay private and are attached by the SDK.

In `api_key` mode, `client.authenticate()` validates local API-key
configuration and `client.logout()` is a no-op.

The context manager calls `close()` on exit. For clients not used as context
managers, call `logout()` when remote session termination is required and
`close()` to release SDK-owned HTTP resources. Repeated cleanup calls are safe.

Authentication and logout failures use the typed exceptions described in
[Errors](errors.md).
