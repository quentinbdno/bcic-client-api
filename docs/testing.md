# Test Coverage Inventory

The unit suite is offline by construction. `tests/unit/conftest.py` rejects live
`httpx` traffic and provides an injected `MockTransport` client factory for
cross-component tests.

## Requirement coverage

| Requirement | Public behavior | Primary tests |
| --- | --- | --- |
| FR-2 | Explicit/environment configuration and validation | `test_client.py` |
| FR-3 | Cached composed endpoint properties | `test_endpoints.py` |
| FR-4–5 | Explicit/lazy authentication and session headers | `test_auth.py` |
| FR-6 | Logout, close, and context management | `test_lifecycle.py` |
| FR-7–9 | Request construction and JSON/parser boundaries | `test_transport.py` |
| FR-10–12 | Retries and mapped SDK exceptions | `test_errors_retry.py` |
| FR-13 | Controlled generic method execution | `test_methods_endpoint.py` |
| FR-14–15 | Record reads, pages, and writes | `test_endpoints_records.py` |
| FR-16 | Roles and role/user permissions | `test_endpoints_users.py` |
| FR-17 | Buffered binary reads/uploads and limits | `test_endpoints_binary.py` |
| FR-18–20 | Typed pages, traversal, and models | `test_pagination.py`, `test_models.py` |
| FR-21 | Typed public signatures | strict mypy and domain tests |
| FR-22 | Operational logging and redaction | `test_logging.py` |
| FR-23 | Injectable HTTP and no-network enforcement | `test_fakes.py` |

`test_public_behavior_contract.py` supplements the focused modules with
cross-component error-boundary and sensitive-representation checks. The
exception matrices cover configuration, validation, authentication,
authorization, not-found, rate-limit, server, network, generic API, and
pagination-limit outcomes. Boundary tests also cover malformed responses,
retry exhaustion, pagination stalls/limits, denied or missing resources,
invalid models, binary encoding, and binary size limits.

## Local gates

Run the complete behavioral baseline with:

```console
poetry run pytest
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy
```
