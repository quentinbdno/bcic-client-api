---
title: "Product Brief: bcic-client-api"
status: draft
created: 2026-07-08
updated: 2026-07-08
---

# Product Brief: bcic-client-api

## Executive Summary

`bcic-client-api` is a reusable Python SDK for the Infinite Blue Business Continuity in the Cloud (BCIC) REST API. It is not an application, CLI, dashboard, reporting tool, or synchronization workflow. Its job is to become the canonical Python interface that downstream automation scripts, services, migration tools, and reporting projects import when they need to interact with BCIC.

The SDK should completely abstract direct HTTP usage. A developer should be able to authenticate, retrieve data, create or update records, handle pagination, and respond to API errors through clean Python objects and methods without reading the REST documentation or constructing URLs manually.

The product bet is maintainability over cleverness. Because this SDK will sit underneath future organizational tooling, the architecture must preserve backwards compatibility, isolate generated or API-derived code behind a stable public API, and make new BCIC domains easy to add without modifying unrelated modules.

## The Problem

Future BCIC automation will otherwise repeat the same fragile integration work: building URLs, attaching credentials, handling expired sessions, parsing JSON or XML responses, interpreting permission errors, managing pagination, and translating API concepts into Python code. That repetition creates inconsistent behavior, scattered authentication logic, harder testing, and high migration cost whenever the BCIC API changes.

The official Infinite Blue documentation exposes a broad API surface. The first implementation should prioritize the REST v1 method-style API under `/rest/api/{method_name}`. REST API v2.0, which includes Record, User, Admin, System, and custom method resources, should remain visible in the architecture but secondary to the v1-first roadmap.

## The Solution

Build a production-quality Python 3.12+ library organized around a small public `Client` and cohesive endpoint modules:

```python
from bcic import Client

client = Client(...)

plans = client.plans.list()
plan = client.plans.get(id)
client.contacts.create(...)
client.users.update(...)
```

The user-facing API should expose domain operations, not transport details. Internally, authentication, token refresh, retry policy, request construction, response parsing, exception mapping, pagination, logging, and model validation should be separate concerns.

The target implementation stack is Python 3.12+, Poetry, `httpx`, Pydantic v2, `pytest`, `python-dotenv`, `tenacity`, standard `typing`, Ruff, and mypy.

Where an OpenAPI or Swagger specification is available, it should be treated as source of truth for endpoint and schema generation. Generated models or clients must remain isolated behind the hand-written SDK surface so regeneration after BCIC API updates does not break downstream projects.

The initial SDK should focus on REST v1 coverage first. REST v2 support should be designed as a future-compatible extension, not the first release driver.

## Design Principles

- Clean public API: callers use `client.<domain>.<operation>()`, not raw URLs or HTTP requests.
- SOLID, clean architecture where appropriate, and composition over inheritance.
- Strong typing throughout, including endpoint inputs, response models, pagination helpers, and exceptions.
- No business logic in the HTTP layer.
- Small cohesive modules: `client.py`, `auth.py`, `config.py`, `exceptions.py`, `pagination.py`, `transport.py`, `models/`, `endpoints/`, and `utils/`.
- Typed Pydantic models whenever practical, with escape hatches only where BCIC payloads are dynamic.
- Standard-library logging only; no `print()`.
- Public methods documented with docstrings.

## Who This Serves

- Python developers building internal BCIC automation who need a reliable SDK rather than hand-written HTTP calls.
- Service owners integrating BCIC data into other systems.
- Migration and synchronization engineers who need stable read/write primitives but will implement business workflows outside this library.
- Reporting and analytics projects that need to retrieve BCIC records without learning the full REST API surface.

## Success Criteria

- A developer unfamiliar with the BCIC REST API can install the package, authenticate, retrieve data, create or update records, and handle errors without reading the REST documentation.
- HTTP exceptions and raw transport errors never leak directly to SDK users; callers receive SDK-specific exceptions such as `AuthenticationError`, `AuthorizationError`, `ValidationError`, `RateLimitError`, `NotFoundError`, `ServerError`, and `ApiError`.
- Authentication is isolated from endpoint implementations and automatically attaches credentials, refreshes tokens or sessions where needed, and manages client/session lifecycle.
- Pagination is abstracted with helpers such as `list_all()` so callers do not manually manage `start` and `count` style paging.
- HTTP calls are mockable and unit tests cover transport behavior, auth behavior, exception mapping, pagination, endpoint methods, and model validation.
- New API domains can be added by adding endpoint modules and models, without rewriting existing endpoint code.
- Documentation includes installation instructions, quick start, authentication guide, examples, and API reference.

## Scope

### In Scope

- Python package structure and build/test/lint/type-check tooling.
- Poetry-based dependency management and packaging.
- Typed configuration and client initialization.
- Authentication/session management.
- HTTP transport wrapper using `httpx`.
- Retry handling using `tenacity`.
- SDK exception hierarchy and API error mapping.
- Pagination primitives and `list_all()` convenience methods.
- Pydantic v2 response/request models where practical.
- Endpoint modules for prioritized BCIC REST v1 methods and domains.
- Unit tests with mockable HTTP calls.
- Developer documentation and examples outside the library package.

### Out of Scope

- GUI.
- CLI.
- Dashboards.
- Reporting workflows.
- Synchronization jobs.
- BCIC-specific business processes.
- Example scripts mixed into library code.

## Source Documentation Notes

- Legacy Platform REST methods are documented by Infinite Blue and use URLs in the form `https://app.infiniteblue.com/rest/api/{method_name}`.
- REST API v2.0 is documented separately and covers Record, User, Admin, System, and custom method APIs.
- REST API v2.0 documents endpoint versioning through the `Accept-Version` header and response `Content-Version` header.
- Record retrieval uses `start` and `count` together for pagination, which directly supports SDK-level pagination helpers.

## Open Questions

- Is an OpenAPI/Swagger JSON specification available behind the Redocly documentation page, or only rendered HTML documentation?
- Which REST v1 methods should define the first release: authentication, records, users, roles/permissions, binary data, search/select, or another subset?
- What authentication mode should be first-class for REST v1: legacy session ID login flow, API key/JWT where available, or multiple strategies?
- Which first endpoint domains matter most for the initial PRD: plans, contacts, users, records, metadata/admin, or another BCIC-specific object set mapped onto REST v1 methods?
- Does the organization need support for both JSON and XML legacy responses, or can v1 support be JSON-only where available?
- What backwards compatibility policy should the SDK promise before version 1.0?
