# Authentication and Lifecycle

## Environment configuration

`Client.from_env()` reads:

- `BCIC_BASE_URL`, `BCIC_USERNAME`, and `BCIC_PASSWORD` (required)
- `BCIC_TIMEOUT` (default `30`)
- `BCIC_MAX_RETRIES` (default `3`)
- `BCIC_RETRY_WAIT_SECONDS` (default `0.5`)
- `BCIC_OUTPUT_FORMAT` (default `json`)

```python
from bcic import Client

with Client.from_env() as client:
    roles = client.users.list_roles()
```

Explicit keyword arguments to `from_env()` take precedence over environment
values. Never commit credentials or place them in URLs.

## Sessions and cleanup

Client construction is offline. Call `client.authenticate()` for eager login,
or let the first operation authenticate lazily. Session IDs stay private and
are attached by the SDK.

The context manager calls `close()` on exit. For clients not used as context
managers, call `logout()` when remote session termination is required and
`close()` to release SDK-owned HTTP resources. Repeated cleanup calls are safe.

Authentication and logout failures use the typed exceptions described in
[Errors](errors.md).
