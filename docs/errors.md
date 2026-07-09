# Errors and Retries

All documented SDK failures derive from `BCICError`:

- `ConfigurationError`: missing or invalid client settings
- `ValidationError`: invalid input, model, or response data
- `PaginationLimitError`: configured page/item safeguard reached
- `AuthenticationError`: login or session establishment failed
- `AuthorizationError`: permission denied
- `NotFoundError`: resource not found
- `RateLimitError`: server rate limit
- `ServerError`: transient server failure
- `NetworkError`: sanitized timeout or network failure
- `APIError`: other API, lifecycle, or response failure

```python
from bcic import Client
from bcic.exceptions import AuthorizationError, BCICError

try:
    with Client.from_env() as client:
        client.users.get_role("ROLE_ORIGINAL_ID")
except AuthorizationError:
    print("The configured user cannot read this role")
except BCICError as error:
    print(f"SDK failure: {error}")
```

Network, rate-limit, and server failures are retried up to `max_retries` after
the initial attempt, with `retry_wait_seconds` between attempts.
Authentication, authorization, validation, and not-found failures are
terminal. Public exceptions and logs are sanitized; do not rely on raw server
payloads being present in messages.
