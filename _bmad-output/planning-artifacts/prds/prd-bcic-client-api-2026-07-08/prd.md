---
title: "PRD: bcic-client-api"
status: draft
created: 2026-07-08
updated: 2026-07-08
source_brief: "../briefs/brief-bcic-client-api-2026-07-08/brief.md"
---

# PRD: bcic-client-api

## 0. Document Purpose

This PRD defines the first product slice for `bcic-client-api`, a reusable Python SDK for the Infinite Blue Business Continuity in the Cloud (BCIC) REST API. It is written for product, architecture, and implementation planning. Requirements are grouped by capability with globally stable FR IDs. Inferred details are marked with `[ASSUMPTION: ...]` and repeated in the Assumptions Index.

The PRD builds on the product brief at `_bmad-output/planning-artifacts/briefs/brief-bcic-client-api-2026-07-08/brief.md`. The user has explicitly prioritized the BCIC REST v1 method-style API before REST v2.

## 1. Vision

`bcic-client-api` should become the canonical Python interface for BCIC inside the organization. Downstream scripts and services should import the SDK, configure a client, call domain methods, receive typed Python objects, and handle SDK-specific exceptions without manually constructing REST requests.

The first release should make REST v1 safe and pleasant to use. The SDK should hide v1 transport concerns such as `/rest/api/{method_name}` URLs, session identifiers, output format handling, response status parsing, retries, and pagination helpers. REST v2 remains a future-compatible extension point, not the MVP driver.

The product is infrastructure. Success is not measured by a visible user interface; it is measured by fewer duplicated integration helpers, clearer automation code, and confidence that future BCIC tooling can build on a stable SDK contract.

## 2. Target User

### 2.1 Jobs To Be Done

- As a Python developer, I need a typed BCIC SDK so I can retrieve, create, update, and delete BCIC data without writing raw HTTP integration code.
- As an automation engineer, I need consistent authentication, retry, pagination, and error handling so each script does not invent its own BCIC integration behavior.
- As a service owner, I need a stable package contract so BCIC integrations can evolve without breaking every downstream project.
- As a maintainer, I need a modular SDK architecture so new REST methods and BCIC domains can be added without modifying unrelated code.

### 2.2 Non-Users (v1)

- End users of BCIC business workflows.
- Operators expecting a CLI or GUI.
- Analysts expecting dashboards or reporting logic.
- Teams needing a complete synchronization product rather than SDK primitives.

### 2.3 Key User Journeys

- **UJ-1. Alex retrieves BCIC records from an automation script.** Alex, a Python developer building an internal automation, installs the SDK, creates a `Client`, authenticates with BCIC, calls a high-level list or search method, receives typed results, and handles any failure through SDK exceptions. Alex never constructs `/rest/api/{method_name}` URLs or interprets raw HTTP errors.

- **UJ-2. Morgan adds a new REST v1 method to the SDK.** Morgan, the SDK maintainer, reads the official BCIC REST v1 documentation for the target method, adds a cohesive endpoint method and typed model coverage, writes transport-mocked unit tests, updates docs, and releases without changing existing endpoint modules.

- **UJ-3. Priya handles a failed BCIC operation safely.** Priya, a service owner consuming the SDK, catches `AuthenticationError`, `AuthorizationError`, `NotFoundError`, `RateLimitError`, or `ApiError` instead of `httpx` exceptions or raw BCIC response payloads, then routes the failure through service-specific recovery logic.

## 3. Glossary

- **BCIC** — Infinite Blue Business Continuity in the Cloud.
- **SDK** — The `bcic-client-api` Python package and its public import surface.
- **Client** — The main public entry point exposed as `from bcic import Client`.
- **Endpoint module** — A cohesive SDK module that groups related BCIC operations behind domain methods.
- **REST v1 method** — A legacy BCIC Platform REST method accessed through `/rest/api/{method_name}`.
- **REST v2 API** — The newer BCIC REST API surface covering Record, User, Admin, System, and custom method resources. Deferred from MVP except for future-compatible architecture.
- **Transport layer** — The internal HTTP wrapper responsible for request execution, retry policy, response parsing, and SDK exception mapping.
- **Authentication strategy** — A pluggable component that authenticates with BCIC and attaches required credentials to requests.
- **SDK exception** — A custom exception raised by the SDK instead of leaking raw HTTP or parsing exceptions.
- **Typed model** — A Pydantic v2 model or typed value object used for request and response data.
- **Pagination helper** — SDK behavior that retrieves paged BCIC result sets without requiring callers to manually advance pages.

## 4. Features

### 4.1 Package Foundation and Public Client

**Description:** The SDK provides a Python 3.12+ package with a small, stable public surface centered on `Client`. The package structure separates client orchestration, configuration, authentication, transport, pagination, exceptions, models, endpoint modules, utilities, tests, docs, and examples.

**Functional Requirements:**

#### FR-1: Public package import

Developers can import `Client` from the top-level `bcic` package.

**Consequences (testable):**
- `from bcic import Client` succeeds after installation.
- The top-level package does not expose internal transport or implementation-only modules as primary API.

#### FR-2: Client initialization

Developers can create a `Client` with explicit configuration values and environment-derived configuration.

**Consequences (testable):**
- Client creation supports base URL, credentials or authentication strategy, timeout, retry configuration, and default output format.
- Environment loading supports `python-dotenv` without requiring it at import time.
- Invalid configuration raises a typed SDK validation/configuration error before the first API call.
- Project metadata, dependency groups, package build settings, and tool configuration are managed through Poetry.

#### FR-3: Domain endpoint access

Developers can access grouped endpoint modules from `Client` properties.

**Consequences (testable):**
- Example shape supports `client.records`, `client.users`, and lower-level `client.methods` for REST v1 method coverage. `[ASSUMPTION: The MVP domain groups should start with records, users, and generic methods because the exact BCIC object domains such as plans or contacts are not yet confirmed.]`
- Endpoint modules receive shared auth, transport, logging, and configuration through composition.
- Adding a new endpoint module does not require modifying existing endpoint module implementations.

### 4.2 REST v1 Authentication and Session Management

**Description:** Authentication is isolated from endpoint implementations. REST v1 authentication should support the documented login/logout method flow and keep session attachment out of domain methods. `[ASSUMPTION: REST v1 MVP should start with session-based login/logout because the v1 documentation examples show `sessionId` usage.]`

**Functional Requirements:**

#### FR-4: Login flow

The SDK authenticates against BCIC REST v1 and stores the resulting session information internally.

**Consequences (testable):**
- Authentication can be triggered explicitly or lazily before the first request.
- Endpoint methods do not accept or manually concatenate `sessionId`.
- Authentication failures raise `AuthenticationError`.

#### FR-5: Credential attachment

The SDK attaches required REST v1 authentication parameters or headers to outbound requests.

**Consequences (testable):**
- Auth data is attached consistently by the authentication strategy or transport layer.
- Endpoint modules do not duplicate auth parameter logic.
- Sensitive values are not included in normal log output.

#### FR-6: Logout and session lifecycle

The SDK supports explicit session cleanup and safe client closing.

**Consequences (testable):**
- `Client.close()` releases the underlying HTTP client resources.
- A logout operation calls the appropriate BCIC REST v1 method when a session exists.
- Calling close/logout more than once is safe.

### 4.3 REST v1 Transport and Response Handling

**Description:** The transport layer executes HTTP calls through `httpx`, applies retry policy, parses BCIC REST v1 responses, maps errors to SDK exceptions, and returns normalized data to endpoint modules.

**Functional Requirements:**

#### FR-7: Method-style request abstraction

Endpoint modules can execute REST v1 methods by method name and typed parameters without constructing URLs.

**Consequences (testable):**
- The transport builds requests against `/rest/api/{method_name}`.
- Parameters can be sent using GET query parameters or POST bodies according to endpoint needs.
- The public SDK does not require callers to pass raw URLs.

#### FR-8: JSON-first response parsing

The SDK supports JSON responses for REST v1 methods where available.

**Consequences (testable):**
- Parsed responses are normalized before model validation.
- Malformed responses raise a typed `ApiError` or parsing-specific SDK exception.
- `[ASSUMPTION: MVP can be JSON-first, while XML support remains an open scope decision.]`

#### FR-9: XML compatibility boundary

The SDK design allows XML response support to be added without changing public endpoint method names.

**Consequences (testable):**
- Output format is represented in configuration or per-request options, not hard-coded in endpoint modules.
- XML parsing support can be implemented behind the transport/response parser boundary.
- Open XML-specific model gaps are documented when unsupported.

#### FR-10: Retry policy

The SDK retries retryable failures according to configurable policy.

**Consequences (testable):**
- Retry behavior is implemented with `tenacity`.
- Retry defaults are conservative and documented.
- Authentication, validation, and permission errors are not retried by default.

### 4.4 SDK Error Model

**Description:** SDK users should never catch raw `httpx` exceptions or parse raw BCIC error payloads for normal control flow. The SDK exposes a custom exception hierarchy.

**Functional Requirements:**

#### FR-11: Exception hierarchy

The SDK provides custom exceptions for authentication, authorization, validation, rate limit, not found, server, and generic API failures.

**Consequences (testable):**
- Exceptions include `AuthenticationError`, `AuthorizationError`, `ValidationError`, `RateLimitError`, `NotFoundError`, `ServerError`, and `ApiError`.
- All SDK exceptions inherit from a common base exception.
- Exceptions preserve useful context such as method name, status code or BCIC status, and sanitized response detail.

#### FR-12: Error mapping

The transport maps HTTP failures and BCIC response statuses to SDK exceptions.

**Consequences (testable):**
- `httpx` timeout/network exceptions are wrapped in SDK exceptions.
- BCIC login/session failures map to `AuthenticationError`.
- Permission failures map to `AuthorizationError`.
- Unknown API failures map to `ApiError` with sanitized context.

### 4.5 Endpoint Coverage for MVP

**Description:** MVP endpoint coverage should provide enough REST v1 surface for downstream projects to authenticate and perform core data operations. The exact domain nouns are not fully confirmed, so the PRD defines a conservative first slice anchored in documented REST v1 method categories.

**Functional Requirements:**

#### FR-13: Generic REST v1 method client

Developers can call a controlled generic REST v1 method wrapper for documented methods not yet promoted to domain-specific endpoint modules.

**Consequences (testable):**
- `client.methods.call(...)` or equivalent accepts a method name and typed parameter payload. `[ASSUMPTION: A controlled generic method client is needed to avoid blocking early adopters while domain modules mature.]`
- The generic method wrapper still applies auth, retries, response parsing, logging, and exception mapping.
- The generic method wrapper is documented as lower-level than domain modules.

#### FR-14: Record read operations

Developers can retrieve records and record-related data through high-level methods.

**Consequences (testable):**
- SDK methods cover at least single-record retrieval and paged/list retrieval using documented REST v1 method equivalents such as `getRecord`, `getPage`, `search`, or `selectQuery`. `[ASSUMPTION: The exact method set will be confirmed against official REST v1 method pages during architecture/story creation.]`
- Returned records are represented as typed models or typed mapping models where object schemas are dynamic.
- Callers do not manually construct query strings.

#### FR-15: Record write operations

Developers can create, update, and delete records through high-level methods.

**Consequences (testable):**
- SDK methods cover REST v1 create/update/delete operations for records.
- Validation catches clearly invalid local inputs before transport execution where practical.
- BCIC validation errors map to SDK `ValidationError`.

#### FR-16: User and permission read operations

Developers can retrieve basic user, role, and permission data needed by common automation.

**Consequences (testable):**
- SDK methods cover documented REST v1 methods such as `getRoles`, `getRoleById`, `getPermissionsByRole`, and `getPermissionsByUser` where applicable.
- Permission failures are represented through SDK exceptions, not raw response payloads.
- `[ASSUMPTION: User/role/permission reads are in MVP; mutating user/permission operations may be deferred unless confirmed.]`

#### FR-17: Binary data operations

Developers can retrieve and upload binary data when supported by REST v1.

**Consequences (testable):**
- SDK methods cover `getBinaryData` and `setBinaryData` or documented equivalents.
- Binary methods stream or buffer data according to documented size constraints. `[ASSUMPTION: Size limits are unknown and must be confirmed before implementation.]`
- Binary operations do not log payload contents.

### 4.6 Pagination and Bulk Retrieval

**Description:** The SDK provides pagination helpers so callers can retrieve complete result sets without manual page advancement. REST v1 method-specific pagination should be normalized into a common SDK pattern.

**Functional Requirements:**

#### FR-18: Page abstraction

The SDK exposes a typed page abstraction for paged responses.

**Consequences (testable):**
- Page objects expose items and pagination metadata where available.
- Page behavior is independent of the underlying REST method name.
- Dynamic record payloads remain typed enough for downstream code to reason about IDs and field values.

#### FR-19: List-all helper

The SDK exposes helpers that fetch all pages for list/search operations.

**Consequences (testable):**
- `list_all()` or equivalent repeatedly fetches pages until completion.
- The helper has configurable page size and maximum item/page safeguards.
- Retry and exception behavior is consistent across every page request.

### 4.7 Models and Typing

**Description:** Pydantic v2 models and strong typing make SDK behavior predictable while allowing BCIC dynamic object fields where necessary.

**Functional Requirements:**

#### FR-20: Common response models

The SDK defines common models for REST v1 response envelopes, records, users, roles, permissions, binary metadata, and pagination results where practical.

**Consequences (testable):**
- Public endpoint methods return typed models or typed collections.
- Dynamic BCIC record fields use a deliberate typed mapping model, not unstructured `Any` everywhere.
- Model validation errors are surfaced as SDK validation errors when they affect public SDK behavior.

#### FR-21: Request models and typed parameters

Endpoint methods use typed parameters and request models where practical.

**Consequences (testable):**
- Public methods have type annotations suitable for mypy.
- Common request options such as output format, timeout override, page size, and filters are typed.
- Public docstrings describe parameter meaning and return types.

### 4.8 Logging, Testing, and Documentation

**Description:** The SDK must be easy to operate, test, and learn. Logging uses the standard Python logging module. Tests mock HTTP calls. Documentation supports installation, authentication, examples, and API reference.

**Functional Requirements:**

#### FR-22: Logging

The SDK logs useful operational events without exposing secrets or payloads by default.

**Consequences (testable):**
- The SDK uses `logging.getLogger(...)`, never `print()`.
- Log level is configurable by the consuming application.
- Credentials, session IDs, tokens, and binary payloads are redacted.

#### FR-23: Testability

The SDK is designed for unit testing with mockable HTTP calls.

**Consequences (testable):**
- Tests can inject an `httpx` mock transport or equivalent.
- Unit tests cover auth, transport, retries, exception mapping, pagination, models, and endpoint methods.
- No unit test depends on live BCIC credentials or a live BCIC tenant.

#### FR-24: Developer documentation

The project includes human-facing documentation and examples outside library code.

**Consequences (testable):**
- Documentation includes installation, quick start, authentication guide, error handling guide, pagination guide, and API reference.
- Examples live under `examples/`, not inside `bcic/`.
- Every public method has a docstring.

## 5. Non-Goals (Explicit)

- No GUI.
- No CLI.
- No dashboarding.
- No reporting workflows.
- No synchronization jobs.
- No BCIC business workflow implementation.
- No example scripts mixed with library code.
- No REST v2-first implementation.
- No direct exposure of raw HTTP requests as the main user experience.

## 6. MVP Scope

### 6.1 In Scope

- Python 3.12+ package foundation.
- Poetry-based dependency management and packaging.
- `Client` public entry point.
- Configuration loading and validation.
- REST v1 authentication/session strategy.
- `httpx` transport wrapper.
- `tenacity` retry policy.
- REST v1 method-style request abstraction.
- JSON-first response parsing.
- SDK exception hierarchy and error mapping.
- Generic REST v1 method wrapper.
- Initial high-level endpoint modules for records and selected user/role/permission reads. `[ASSUMPTION: Records plus read-only user/role/permission support are enough to define the first useful SDK slice.]`
- Pagination/page helpers.
- Pydantic v2 common models.
- Logging.
- Unit tests with mocked HTTP.
- Installation, quick start, authentication, error handling, pagination, and API reference docs.

### 6.2 Out of Scope for MVP

- REST v2 endpoint implementation; defer to later once v1 foundation is stable.
- Full generated client from REST v2 OpenAPI/Swagger; defer until source spec availability is confirmed.
- XML-first implementation; defer unless v1 JSON support proves insufficient.
- Mutating user/role/permission administration; defer unless required by first consumers.
- Advanced BCIC workflow abstractions; consuming projects own business workflows.
- Live integration tests against a BCIC tenant; defer until credentials, tenant, and data safety policy are defined.

## 7. API Contracts / Public Surface

- `bcic.Client` is the primary public entry point.
- Public endpoint methods should follow domain-oriented names such as `client.records.get(...)`, `client.records.search(...)`, `client.records.create(...)`, `client.records.update(...)`, `client.records.delete(...)`, `client.users.get(...)`, and `client.methods.call(...)`.
- The SDK may expose lower-level escape hatches, but they must remain clearly documented as lower-level than domain methods.
- Public methods must avoid requiring raw URLs, raw `httpx` objects, or manual session parameter handling.
- Public return values should be typed Pydantic models, typed collections, typed page objects, or explicitly documented primitives.

## 8. Cross-Cutting NFRs

### 8.1 Maintainability

- Modules are small and cohesive.
- Auth, transport, endpoint logic, models, pagination, exceptions, and configuration remain separate.
- New endpoint modules can be added without modifying unrelated endpoint modules.
- Generated or API-derived code, if introduced, remains isolated from the hand-written public API.

### 8.2 Reliability

- Retry behavior is deterministic and configurable.
- SDK exceptions preserve enough sanitized context for debugging.
- Client/session lifecycle is explicit and safe.
- Network and parsing failures do not leak as raw `httpx` or parser exceptions.

### 8.3 Typing and Quality Gates

- The codebase uses strong type annotations.
- mypy passes for library code.
- Ruff passes for linting/formatting.
- Tests are mandatory for public behavior.

### 8.4 Security

- Credentials, session IDs, tokens, and binary payloads are redacted from logs and exceptions.
- `.env` support must not encourage committing secrets.
- Authentication state is encapsulated and not exposed casually through public attributes.

### 8.5 Documentation Quality

- Every public method has a docstring.
- Documentation examples show realistic SDK usage without live secrets.
- Docs distinguish high-level endpoint modules from lower-level generic method access.

## 9. Language / Runtime Targets and Dependency Policy

- Runtime target: Python 3.12+.
- Dependency manager and packaging workflow: Poetry.
- `pyproject.toml` is the source of truth for package metadata, runtime dependencies, development dependency groups, Ruff configuration, mypy configuration, and pytest configuration where practical.
- `poetry.lock` should be committed to keep SDK development, CI, and test environments reproducible; published package compatibility is governed by dependency constraints in `pyproject.toml`.
- Required runtime dependencies: `httpx`, Pydantic v2, `tenacity`, and typing support from the standard library.
- Optional/runtime-adjacent dependency: `python-dotenv` for local development configuration.
- Development dependencies: `pytest`, Ruff, mypy.
- Dependency additions require a clear SDK-level reason and should not be introduced for convenience alone.

## 10. Versioning and Deprecation Policy

- Before `1.0`, public API changes are allowed but must be documented in release notes.
- After `1.0`, public endpoint methods, models, and exception names should follow semantic versioning.
- Breaking changes require a major version bump after `1.0`.
- Deprecated public methods should emit documented deprecation warnings for at least one minor release before removal. `[ASSUMPTION: The organization wants SemVer-style stability; no internal versioning policy has been provided yet.]`

## 11. Success Metrics

**Primary**

- **SM-1:** First useful automation path works end-to-end in local tests: authenticate, retrieve records, create/update/delete a testable record payload through mocked transport, and handle errors. Validates FR-4, FR-7, FR-11, FR-14, FR-15, FR-23.
- **SM-2:** SDK users do not write raw BCIC URLs for supported MVP operations. Validates FR-1, FR-3, FR-7, FR-13, FR-14, FR-15.
- **SM-3:** Library quality gates pass: unit tests, Ruff, and mypy. Validates FR-20, FR-21, FR-23.

**Secondary**

- **SM-4:** Documentation lets a new developer install, authenticate, retrieve records, create/update data, use pagination, and catch errors without reading BCIC REST documentation. Validates FR-22, FR-24.
- **SM-5:** A new REST v1 method can be added with a focused endpoint/model/test change and no changes to unrelated endpoint modules. Validates FR-3, FR-13, FR-20.

**Counter-metrics (do not optimize)**

- **SM-C1:** Do not maximize endpoint count at the expense of tested behavior and stable contracts. Counterbalances SM-2.
- **SM-C2:** Do not expose raw transport escape hatches as the default path just to accelerate implementation. Counterbalances SM-1.

## 12. Source Documentation Notes

- Official REST v1 documentation: `https://documentation.infiniteblue.com/platform/platform_rest_methods.htm`.
- Official REST v2 documentation: `https://documentation.infiniteblue.com/platform/restapiv2.html`.
- REST v1 documentation states that methods are accessed through `/rest/api/{method_name}`, and parameters can be supplied through GET URL parameters or POST request bodies.
- REST v1 documentation shows XML examples and describes XML or JSON result/error responses.
- REST v2 documentation shows newer Record, Admin, System, Users, userResource, and customMethod API groups; this PRD defers REST v2 implementation from MVP.

## 13. Open Questions

1. Which exact REST v1 methods must be in the MVP beyond login/logout, record read/write, search/select, and basic role/permission reads?
2. Does the organization require XML response support in MVP, or can MVP be JSON-first with XML-compatible architecture?
3. Which BCIC object domains map to first-class SDK modules first: generic records, plans, contacts, users, or another organization-specific object set?
4. What BCIC tenant or sandbox will be used for future live integration testing?
5. What authentication modes are required for REST v1 in real deployments: session login only, API key/JWT where available, or multiple strategies?
6. What naming convention should domain modules use when BCIC object names differ between tenants or applications?
7. What compatibility promise should be made before version `1.0`?

## 14. Assumptions Index

- §4.1 / FR-3 — The MVP domain groups should start with records, users, and generic methods because the exact BCIC object domains such as plans or contacts are not yet confirmed.
- §4.2 — REST v1 MVP should start with session-based login/logout because the v1 documentation examples show `sessionId` usage.
- §4.3 / FR-8 — MVP can be JSON-first, while XML support remains an open scope decision.
- §4.5 / FR-13 — A controlled generic method client is needed to avoid blocking early adopters while domain modules mature.
- §4.5 / FR-14 — The exact record method set will be confirmed against official REST v1 method pages during architecture/story creation.
- §4.5 / FR-16 — User/role/permission reads are in MVP; mutating user/permission operations may be deferred unless confirmed.
- §4.5 / FR-17 — Binary data size limits are unknown and must be confirmed before implementation.
- §6.1 — Records plus read-only user/role/permission support are enough to define the first useful SDK slice.
- §10 — The organization wants SemVer-style stability; no internal versioning policy has been provided yet.
