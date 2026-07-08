---
stepsCompleted:
  - step-01-validate-prerequisites
  - step-02-design-epics
  - step-03-create-stories
  - step-04-final-validation
inputDocuments:
  - "_bmad-output/planning-artifacts/prds/prd-bcic-client-api-2026-07-08/prd.md"
  - "_bmad-output/planning-artifacts/architecture/architecture-bcic-client-api-2026-07-08/ARCHITECTURE-SPINE.md"
  - "_bmad-output/planning-artifacts/briefs/brief-bcic-client-api-2026-07-08/brief.md"
---

# bcic-client-api - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for bcic-client-api, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR-1: Developers can import `Client` from the top-level `bcic` package, and internal transport or implementation-only modules are not presented as the primary API.

FR-2: Developers can create a `Client` with explicit and environment-derived configuration for base URL, credentials or auth strategy, timeout, retry configuration, and default output format; invalid configuration raises a typed SDK configuration or validation error before the first API call where practical; Poetry manages metadata, dependencies, build settings, and tool configuration.

FR-3: Developers can access grouped endpoint modules from `Client` properties, including `client.records`, `client.users`, and lower-level `client.methods`; endpoint modules receive shared auth, transport, logging, and configuration through composition; new endpoint modules can be added without modifying existing endpoint implementations.

FR-4: The SDK authenticates against BCIC REST v1, stores resulting session information internally, supports explicit or lazy authentication before the first request, keeps `sessionId` handling out of endpoint methods, and raises `AuthenticationError` on authentication failure.

FR-5: The SDK attaches required REST v1 authentication parameters or headers consistently through the authentication strategy or transport layer; endpoint modules do not duplicate auth parameter logic; sensitive values are not included in normal log output.

FR-6: The SDK supports explicit session cleanup and safe client closing, including `Client.close()` releasing HTTP resources, logout calling the appropriate REST v1 method when a session exists, and repeated close/logout calls being safe.

FR-7: Endpoint modules can execute REST v1 methods by method name and typed parameters without constructing URLs; the transport builds requests against `/rest/api/{method_name}` and supports GET query parameters or POST bodies according to endpoint needs.

FR-8: The SDK supports JSON responses for REST v1 methods where available, normalizes parsed responses before model validation, and raises typed SDK errors for malformed responses.

FR-9: The SDK design allows XML response support to be added without changing public endpoint method names by keeping output format in configuration or per-request options and behind the transport/response parser boundary.

FR-10: The SDK retries retryable failures using configurable `tenacity` policy with conservative documented defaults; authentication, validation, and permission errors are not retried by default.

FR-11: The SDK provides custom exceptions for authentication, authorization, validation, rate limit, not found, server, and generic API failures; all SDK exceptions inherit from a common base and preserve useful sanitized context.

FR-12: The transport maps HTTP failures, BCIC response statuses, network exceptions, timeout exceptions, login/session failures, permission failures, and unknown API failures to SDK exceptions.

FR-13: Developers can call a controlled generic REST v1 method wrapper for documented methods not yet promoted to domain-specific endpoint modules; the wrapper still applies auth, retries, parsing, logging, and exception mapping and is documented as lower-level than domain modules.

FR-14: Developers can retrieve records and record-related data through high-level methods covering at least single-record retrieval and paged/list retrieval using documented REST v1 equivalents such as `getRecord`, `getPage`, `search`, or `selectQuery`; returned records use typed models or typed mapping models and callers do not manually construct query strings.

FR-15: Developers can create, update, and delete records through high-level methods; local validation catches clearly invalid inputs where practical and BCIC validation errors map to SDK `ValidationError`.

FR-16: Developers can retrieve basic user, role, and permission data needed by common automation through documented REST v1 methods such as `getRoles`, `getRoleById`, `getPermissionsByRole`, and `getPermissionsByUser`; permission failures are exposed through SDK exceptions.

FR-17: Developers can retrieve and upload binary data through REST v1 methods such as `getBinaryData` and `setBinaryData`; binary methods stream or buffer according to documented size constraints and do not log payload contents.

FR-18: The SDK exposes a typed page abstraction for paged responses, including items and pagination metadata where available; page behavior is independent of the underlying REST method name and dynamic record payloads remain typed enough for downstream code to reason about IDs and field values.

FR-19: The SDK exposes `list_all()` or equivalent helpers that repeatedly fetch pages until completion with configurable page size and maximum item/page safeguards; retry and exception behavior is consistent across every page request.

FR-20: The SDK defines common Pydantic v2 models for REST v1 response envelopes, records, users, roles, permissions, binary metadata, and pagination results where practical; public endpoint methods return typed models or typed collections; dynamic BCIC record fields use deliberate typed mapping models; model validation errors surface as SDK validation errors when they affect public SDK behavior.

FR-21: Endpoint methods use typed parameters and request models where practical, including annotations suitable for mypy, typed common request options, and docstrings that describe parameter meaning and return types.

FR-22: The SDK logs useful operational events using `logging.getLogger(...)` without `print()`, lets consuming applications configure log level, and redacts credentials, session IDs, tokens, and binary payloads.

FR-23: The SDK is designed for unit testing with mockable HTTP calls, injectable `httpx` mock transport or equivalent, and unit coverage for auth, transport, retries, exception mapping, pagination, models, and endpoint methods; no unit test depends on live BCIC credentials or a live tenant.

FR-24: The project includes human-facing documentation and examples outside library code, including installation, quick start, authentication guide, error handling guide, pagination guide, API reference, examples under `examples/`, and docstrings on every public method.

### NonFunctional Requirements

NFR-1: The SDK must be maintainable through small cohesive modules that keep auth, transport, endpoint logic, models, pagination, exceptions, and configuration separate.

NFR-2: New endpoint modules must be addable without modifying unrelated endpoint modules.

NFR-3: Generated or API-derived code, if introduced, must remain isolated from the hand-written public API.

NFR-4: Retry behavior must be deterministic and configurable.

NFR-5: SDK exceptions must preserve enough sanitized context for debugging while preventing raw transport and parser failures from leaking as public control-flow errors.

NFR-6: Client and session lifecycle must be explicit and safe.

NFR-7: The codebase must use strong type annotations, and mypy must pass for library code.

NFR-8: Ruff linting and formatting must pass.

NFR-9: Tests are mandatory for public behavior.

NFR-10: Credentials, session IDs, tokens, and binary payloads must be redacted from logs and exceptions.

NFR-11: `.env` support must not encourage committing secrets.

NFR-12: Authentication state must be encapsulated and not exposed casually through public attributes.

NFR-13: Every public method must have a docstring.

NFR-14: Documentation examples must show realistic SDK usage without live secrets.

NFR-15: Documentation must distinguish high-level endpoint modules from lower-level generic method access.

NFR-16: The runtime target is Python 3.12+.

NFR-17: Poetry must be the dependency manager and packaging workflow; `pyproject.toml` is the source of truth for metadata, dependency groups, and tool configuration where practical.

NFR-18: `poetry.lock` should be committed for reproducible development and CI.

NFR-19: Required runtime dependencies are `httpx`, Pydantic v2, `tenacity`, and standard-library typing support; `python-dotenv` is optional/runtime-adjacent for local configuration.

NFR-20: Development dependencies are `pytest`, Ruff, and mypy.

NFR-21: New dependencies require a clear SDK-level reason and must not be introduced for convenience alone.

NFR-22: Before `1.0`, public API changes are allowed but must be documented in release notes; after `1.0`, public endpoint methods, models, and exception names should follow semantic versioning.

NFR-23: Breaking changes after `1.0` require a major version bump, and deprecated public methods should emit documented deprecation warnings for at least one minor release before removal.

### Additional Requirements

- Use a hexagonal SDK architecture where the public `Client` and endpoint modules are the application-facing API, while authentication, REST v1 transport, response parsing, retry behavior, and logging are internal adapters.
- Supported operations must be exposed through domain-first endpoint properties such as `client.records`, `client.users`, `client.binary`, and `client.methods`; `client.methods` is a documented lower-level escape hatch.
- Endpoint modules must call the transport boundary with REST v1 method names plus typed parameters or request models; only the transport builds method-style REST v1 requests.
- `auth.py` must own authentication strategies and session state; the transport asks the strategy to authenticate and attach credentials.
- External failures crossing the public API must be mapped to the SDK exception hierarchy with sanitized context before leaving the SDK.
- Public methods must return Pydantic models, typed page objects, or typed mappings; unrestricted `Any` should remain at parser boundaries only.
- Page state and `list_all()` traversal must live in `pagination.py` and shared helpers rather than endpoint-specific traversal loops.
- `pyproject.toml` must centralize package metadata, Poetry dependency groups, Ruff, mypy, and pytest configuration where practical.
- Transport creation must support injection of an `httpx` client, transport, or equivalent test seam for mocked unit tests.
- REST v2 implementation is deferred and must later enter through separate transport/endpoint adapters while preserving the `Client` public contract.
- Parser behavior must be JSON-first for MVP while keeping output format as a transport/parser concern so XML can be added behind the same endpoint method names.
- Use module names and structure from the architecture seed: `bcic/__init__.py`, `client.py`, `config.py`, `auth.py`, `transport.py`, `pagination.py`, `exceptions.py`, `models/`, `endpoints/`, `utils/`, `tests/unit/`, `docs/`, and `examples/`.
- REST v1 method names must stay in endpoint constants or method metadata, not scattered inline across call sites.
- Logging must use `logging.getLogger(__name__)` and redact credentials, session IDs, tokens, and binary payloads.
- Dynamic records must use typed record containers with stable fields for object name, record ID, and field mapping.
- Unit tests must not make live BCIC calls.
- Exact REST v1 method inventory, XML implementation, REST v2 adapter architecture, live integration tests, and organization-specific first-class domain modules are deferred.
- The brief reinforces that the SDK is not an application, CLI, dashboard, reporting tool, synchronization workflow, or BCIC business process implementation.
- The brief states that OpenAPI/Swagger, if available, should be treated as source of truth for endpoint and schema generation, with generated code isolated behind the handwritten SDK surface.

### UX Design Requirements

No UX design contract was found in `_bmad-output/planning-artifacts`; no UX design requirements were extracted.

### FR Coverage Map

FR-1: Epic 1 - Top-level `Client` import.

FR-2: Epic 1 - Client configuration and Poetry package setup.

FR-3: Epic 1 - Domain endpoint access from `Client`.

FR-4: Epic 2 - REST v1 login/session authentication.

FR-5: Epic 2 - Credential attachment.

FR-6: Epic 2 - Logout and safe client closing.

FR-7: Epic 2 - `/rest/api/{method_name}` request abstraction.

FR-8: Epic 2 - JSON-first response parsing.

FR-9: Epic 2 - XML-compatible parser boundary.

FR-10: Epic 2 - Retry policy.

FR-11: Epic 2 - SDK exception hierarchy.

FR-12: Epic 2 - HTTP/BCIC error mapping.

FR-13: Epic 2 - Controlled generic REST v1 method client.

FR-14: Epic 3 - Record read operations.

FR-15: Epic 3 - Record write operations.

FR-16: Epic 4 - User, role, and permission reads.

FR-17: Epic 4 - Binary data operations.

FR-18: Epic 3 - Page abstraction.

FR-19: Epic 3 - List-all helper.

FR-20: Epics 1, 3, 4 - Common models and typed returns.

FR-21: Epics 1, 3, 4 - Typed parameters and request models.

FR-22: Epics 4, 5 - Redacted logging.

FR-23: Epic 5 - Mockable tests and unit coverage.

FR-24: Epic 5 - Documentation and examples.

## Epic List

### Epic 1: Installable SDK Client Foundation

Developers can install the package, import `bcic.Client`, configure it explicitly or from the environment, and access stable endpoint properties without knowing internal module structure.

**FRs covered:** FR-1, FR-2, FR-3, FR-20, FR-21

### Epic 2: Authenticated REST v1 Method Execution

Developers can authenticate with BCIC REST v1, execute method-style API calls through the SDK, receive normalized JSON-first responses, benefit from retries, and handle failures through SDK exceptions instead of raw HTTP errors.

**FRs covered:** FR-4, FR-5, FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, FR-12, FR-13

### Epic 3: Record Data Automation

Developers can retrieve, search, page through, create, update, and delete BCIC records through high-level typed record methods without constructing URLs, query strings, or pagination loops.

**FRs covered:** FR-14, FR-15, FR-18, FR-19, FR-20, FR-21

### Epic 4: User, Permission, and Binary Operations

Developers can perform the other MVP operational workflows: read user/role/permission data and upload or retrieve binary data through typed SDK methods with safe logging and error handling.

**FRs covered:** FR-16, FR-17, FR-20, FR-21, FR-22

### Epic 5: SDK Adoption, Maintainability, and Release Confidence

Maintainers and consumers can trust, learn, and extend the SDK through mockable tests, redacted operational logging, quality gates, documentation, examples, and public method docstrings.

**FRs covered:** FR-22, FR-23, FR-24

## Epic 1: Installable SDK Client Foundation

Developers can install the package, import `bcic.Client`, configure it explicitly or from the environment, and access stable endpoint properties without knowing internal module structure.

### Story 1.1: Initialize the Installable Python Package

**Requirements:** FR-1, FR-2

As a Python developer,
I want to install and import the BCIC SDK,
So that I can begin integrating BCIC into an application using a conventional Python package.

**Acceptance Criteria:**

**Given** a supported Python 3.12 or later environment
**When** the developer installs the project through Poetry
**Then** the `bcic` package and its runtime dependencies are installed successfully
**And** the project declares `httpx`, Pydantic 2, and `tenacity` as runtime dependencies.

**Given** a development installation
**When** the maintainer installs the development dependency groups
**Then** `pytest`, Ruff, and mypy are available
**And** their baseline configuration is defined in `pyproject.toml`.

**Given** the package is installed
**When** application code runs `from bcic import Client`
**Then** the import succeeds
**And** internal modules are not required as part of the primary public import path.

### Story 1.2: Configure the Client Explicitly and From the Environment

**Requirements:** FR-2

As an SDK consumer,
I want to configure the client through explicit values or environment variables,
So that I can use the same SDK safely in local development, tests, and deployed automation.

**Acceptance Criteria:**

**Given** valid explicit configuration values for the base URL and authentication
**When** the developer creates a `Client`
**Then** the client accepts those values together with optional timeout, retry, and output settings
**And** configuration validation performs no network request.

**Given** required configuration is absent or invalid
**When** the developer creates a `Client`
**Then** creation fails with a typed SDK configuration or validation exception
**And** the exception does not expose authentication secrets.

**Given** valid BCIC environment variables
**When** the developer constructs the client through the environment-based configuration path
**Then** the same validated client configuration is produced
**And** explicitly supported values take precedence according to the documented configuration rules.

**Given** no dotenv integration is installed or enabled
**When** the `bcic` package is imported
**Then** the import succeeds without loading a dotenv file
**And** no environment or secret values are logged during import or configuration.

### Story 1.3: Expose Stable Domain Endpoint Properties

**Requirements:** FR-3

As an SDK consumer,
I want stable endpoint properties on the client,
So that I can discover and use BCIC capabilities without depending on internal modules or transport details.

**Acceptance Criteria:**

**Given** a configured `Client`
**When** the developer accesses its public domain properties
**Then** `client.records`, `client.users`, `client.binary`, and `client.methods` are available
**And** each property returns the corresponding endpoint object.

**Given** any endpoint object exposed by the client
**When** it is created or reused
**Then** it receives shared configuration, transport, authentication, and parsing dependencies through composition
**And** the public API does not expose raw URLs, `httpx` clients, or BCIC session identifiers.

**Given** a new endpoint domain is added later
**When** it is integrated into the client
**Then** existing endpoint implementations do not require modification
**And** BCIC method names remain centralized in constants or endpoint metadata rather than duplicated across request logic.

### Story 1.4: Establish Common Typed Model Foundations

**Requirements:** FR-20, FR-21

As an SDK consumer,
I want common typed response, pagination, and dynamic-record models,
So that SDK results have a predictable shape while still supporting BCIC's variable record fields.

**Acceptance Criteria:**

**Given** common BCIC response metadata or pagination data
**When** it is represented by the SDK
**Then** it uses reusable Pydantic 2 models
**And** public fields have explicit type annotations suitable for mypy validation.

**Given** a BCIC record with a variable object schema
**When** it is represented by the common dynamic-record model
**Then** the model preserves the object name, record identifier, and dynamic field values
**And** unrestricted `Any` usage is confined to documented parser or dynamic-data boundaries.

**Given** invalid data is supplied to a public common model boundary
**When** validation fails
**Then** the SDK exposes a typed validation failure suitable for application handling
**And** authentication secrets or raw sensitive payloads are not included in its message.

## Epic 2: Authenticated REST v1 Method Execution

Developers can authenticate with BCIC REST v1, execute method-style API calls through the SDK, receive normalized JSON-first responses, benefit from retries, and handle failures through SDK exceptions instead of raw HTTP errors.

### Story 2.1: Build the REST v1 Transport and JSON Parser

**Requirements:** FR-7, FR-8, FR-9

As an SDK endpoint developer,
I want a shared transport that executes REST v1 methods and normalizes JSON responses,
So that endpoint modules do not construct URLs or parse raw HTTP responses.

**Acceptance Criteria:**

**Given** a REST v1 method name and typed parameters
**When** the transport executes a GET or POST request
**Then** it builds the request against `/rest/api/{method_name}`
**And** it places parameters in the query string or request body according to the requested HTTP method.

**Given** a successful JSON response from BCIC
**When** the response parser processes it
**Then** it returns a normalized structure suitable for Pydantic model validation
**And** raw `httpx` response objects do not cross the public SDK boundary.

**Given** a response that is empty, malformed, or incompatible with the expected JSON shape
**When** parsing is attempted
**Then** the SDK raises a typed sanitized API or validation exception
**And** the raw parser exception is not exposed as the public control-flow error.

**Given** a future XML parser implementation
**When** it is added behind the parser boundary
**Then** existing public endpoint method names require no changes
**And** output format remains a configuration or per-request concern.

### Story 2.2: Authenticate and Attach Session Credentials

**Requirements:** FR-4, FR-5

As an SDK consumer,
I want the client to authenticate and manage BCIC session credentials internally,
So that I can call endpoint methods without handling session identifiers myself.

**Acceptance Criteria:**

**Given** valid BCIC credentials and explicit authentication
**When** the developer requests authentication
**Then** the configured authentication strategy calls the appropriate REST v1 login method
**And** resulting session information is stored only in encapsulated authentication state.

**Given** valid credentials and lazy authentication enabled
**When** the first authenticated request is executed
**Then** authentication occurs before that request
**And** subsequent requests reuse the active session while it remains valid.

**Given** an active authenticated session
**When** the transport prepares a REST v1 request
**Then** the authentication strategy attaches the required credential parameters or headers
**And** endpoint modules contain no duplicated session or authentication attachment logic.

**Given** rejected credentials, a failed login response, or an unusable session result
**When** authentication is attempted
**Then** the SDK raises `AuthenticationError`
**And** credentials, tokens, and session identifiers are absent from public attributes, logs, and exception messages.

### Story 2.3: Manage Logout and Client Lifecycle

**Requirements:** FR-6

As an SDK consumer,
I want explicit and safe session and HTTP resource cleanup,
So that long-running automation does not leak sessions or network resources.

**Acceptance Criteria:**

**Given** an authenticated client with an active session
**When** the developer calls logout
**Then** the appropriate REST v1 logout method is called
**And** local session state is cleared after the logout outcome is handled.

**Given** a client with no active session
**When** logout is called one or more times
**Then** the operation completes safely without an unnecessary logout request
**And** the client remains in a consistent unauthenticated state.

**Given** an open client
**When** `Client.close()` is called
**Then** owned HTTP resources are released
**And** repeated close calls are safe.

**Given** a client used through its supported context-manager interface
**When** execution leaves the context
**Then** the same close behavior is performed
**And** cleanup does not conceal an exception already raised inside the context.

### Story 2.4: Map Failures and Apply Retry Policy

**Requirements:** FR-10, FR-11, FR-12

As an SDK consumer,
I want predictable typed failures and conservative retries,
So that my application can respond correctly without interpreting HTTP or BCIC internals.

**Acceptance Criteria:**

**Given** an SDK-originated failure
**When** it crosses the public API boundary
**Then** it inherits from a common SDK base exception
**And** authentication, authorization, validation, rate-limit, not-found, server, and generic API failures have distinct exception types.

**Given** an HTTP error, BCIC error status, network failure, timeout, session failure, permission failure, or unknown API failure
**When** the transport handles it
**Then** it maps the failure to the appropriate SDK exception
**And** preserves useful sanitized context without exposing raw sensitive requests or payloads.

**Given** a configured retry policy and a retryable transient failure
**When** a request fails
**Then** `tenacity` retries it according to deterministic configured limits and delays
**And** the final exhausted failure is raised as the appropriate SDK exception.

**Given** an authentication, authorization, validation, permission, or other non-retryable failure
**When** a request fails
**Then** it is not retried by default
**And** a caller can adjust only the retry settings explicitly exposed by configuration.

### Story 2.5: Execute Controlled Generic REST v1 Methods

**Requirements:** FR-13

As an SDK consumer,
I want controlled access to documented REST v1 methods not yet promoted to domain endpoints,
So that I can use broader BCIC capabilities without bypassing SDK safeguards.

**Acceptance Criteria:**

**Given** a configured client and a documented REST v1 method
**When** the developer invokes it through `client.methods`
**Then** the wrapper accepts the method name, typed parameters, supported HTTP method, and optional output settings
**And** the caller does not construct the REST URL or provide a raw `httpx` request.

**Given** a generic method invocation
**When** it is executed
**Then** it uses the shared authentication, transport, retry, parser, logging, and exception-mapping behavior
**And** returns normalized typed data or a documented typed mapping.

**Given** an unsupported HTTP method, invalid method name, or invalid parameter shape
**When** the generic wrapper validates the request
**Then** it raises a typed SDK validation error before network execution where practical
**And** it does not permit arbitrary URL execution outside the configured REST v1 method boundary.

**Given** both a domain-specific endpoint method and generic method access exist for an operation
**When** public API documentation and docstrings describe that operation
**Then** the domain-specific endpoint is identified as the preferred interface
**And** `client.methods` is identified as the lower-level escape hatch.

## Epic 3: Record Data Automation

Developers can retrieve, search, page through, create, update, and delete BCIC records through high-level typed record methods without constructing URLs, query strings, or pagination loops.

### Story 3.1: Retrieve a Single Record

**Requirements:** FR-14, FR-20, FR-21

As an SDK consumer,
I want to retrieve one BCIC record through a typed high-level method,
So that I can use its identifier and dynamic fields without constructing a REST request.

**Acceptance Criteria:**

**Given** a valid object name and record identifier
**When** the developer requests the record through `client.records`
**Then** the endpoint invokes the documented REST v1 record method through the shared transport
**And** returns a typed dynamic-record model containing the object name, record identifier, and field mapping.

**Given** an empty or clearly invalid object name or record identifier
**When** the method validates its inputs
**Then** it raises the SDK `ValidationError` before network execution where practical
**And** its typed parameters and public docstring describe the accepted values and return type.

**Given** BCIC reports that the record does not exist or the response cannot form a valid record
**When** the result is processed
**Then** the SDK raises `NotFoundError` or `ValidationError` as appropriate
**And** no raw transport, parser, or Pydantic exception crosses the public boundary.

### Story 3.2: Retrieve and Search Paged Records

**Requirements:** FR-14, FR-18, FR-20, FR-21

As an SDK consumer,
I want to retrieve or search a page of records using typed options,
So that I can process bounded record sets without manually constructing queries.

**Acceptance Criteria:**

**Given** a valid object name and typed page or search options
**When** the developer requests records through the high-level endpoint
**Then** the endpoint uses an appropriate documented REST v1 method such as `getPage`, `search`, or `selectQuery`
**And** the caller does not construct a URL or raw query string where typed criteria are supported.

**Given** a successful paged response
**When** it is normalized and validated
**Then** the SDK returns a shared typed `Page` containing typed dynamic records and available pagination metadata
**And** page behavior does not expose or depend on the underlying REST method name.

**Given** invalid pagination bounds, unsupported criteria, or malformed page metadata
**When** the request or response is validated
**Then** the SDK raises a typed validation or API exception
**And** does not return a partially valid page.

### Story 3.3: Traverse All Record Pages Safely

**Requirements:** FR-19

As an SDK consumer,
I want a bounded helper that retrieves all matching record pages,
So that I can automate complete data retrieval without writing pagination loops.

**Acceptance Criteria:**

**Given** a valid record listing or search request
**When** the developer invokes `list_all()` or its documented equivalent
**Then** the pagination helper repeatedly requests pages until BCIC indicates completion
**And** returns or yields typed dynamic records without endpoint-specific traversal logic.

**Given** configured page-size, maximum-page, or maximum-item safeguards
**When** traversal reaches a configured limit before natural completion
**Then** traversal stops deterministically with a documented typed result or exception
**And** it does not silently request additional pages.

**Given** a retryable or terminal failure on any page
**When** that page is requested
**Then** the same retry and exception-mapping behavior used by individual requests applies
**And** traversal does not silently skip the failed page or duplicate previously completed page requests.

### Story 3.4: Create Records

**Requirements:** FR-15, FR-20, FR-21

As an SDK consumer,
I want to create a BCIC record using a typed request,
So that I can submit dynamic record fields without manually invoking a REST method.

**Acceptance Criteria:**

**Given** a valid object name and typed record-creation request
**When** the developer calls the high-level create method
**Then** the endpoint passes the corresponding method name and normalized parameters to the shared transport
**And** returns the created typed record or a documented typed creation result.

**Given** a missing object name, empty field set where unsupported, or clearly invalid field input
**When** the request is validated
**Then** the SDK raises `ValidationError` before network execution where practical
**And** unrestricted dynamic values remain confined to the deliberate record-field mapping boundary.

**Given** BCIC rejects the record data
**When** the response is mapped
**Then** the SDK raises `ValidationError` with useful sanitized context
**And** no credentials, session identifiers, or raw sensitive payloads are included.

### Story 3.5: Update Records

**Requirements:** FR-15, FR-20, FR-21

As an SDK consumer,
I want to update selected fields on an existing BCIC record,
So that I can change record data without replacing unrelated fields or building REST parameters.

**Acceptance Criteria:**

**Given** a valid object name, record identifier, and typed non-empty field changes
**When** the developer calls the high-level update method
**Then** only the supplied changes are sent through the documented REST v1 update operation
**And** the method returns the updated typed record or a documented typed update result.

**Given** an empty change set or clearly invalid object name, record identifier, or field input
**When** local validation runs
**Then** the SDK raises `ValidationError` before network execution where practical
**And** no update request is sent.

**Given** BCIC reports a missing record, permission failure, or invalid update
**When** the result is mapped
**Then** the SDK raises `NotFoundError`, `AuthorizationError`, or `ValidationError` as appropriate
**And** preserves only sanitized diagnostic context.

### Story 3.6: Delete Records

**Requirements:** FR-15, FR-20, FR-21

As an SDK consumer,
I want to delete an identified BCIC record through a typed method,
So that I can remove records without constructing low-level method calls.

**Acceptance Criteria:**

**Given** a valid object name and record identifier
**When** the developer calls the high-level delete method
**Then** the endpoint invokes the documented REST v1 delete operation through the shared transport
**And** returns a documented typed deletion result.

**Given** an empty or clearly invalid object name or record identifier
**When** local validation runs
**Then** the SDK raises `ValidationError` before network execution where practical
**And** no deletion request is sent.

**Given** BCIC reports a missing record, permission failure, validation failure, or server failure
**When** the result is processed
**Then** the corresponding SDK exception is raised
**And** the public method does not expose raw HTTP or BCIC error structures.

## Epic 4: User, Permission, and Binary Operations

Developers can perform the other MVP operational workflows: read user/role/permission data and upload or retrieve binary data through typed SDK methods with safe logging and error handling.

### Story 4.1: Retrieve Roles

**Requirements:** FR-16, FR-20, FR-21

As an SDK consumer,
I want to retrieve BCIC roles through typed high-level methods,
So that I can inspect authorization structures without constructing generic REST calls.

**Acceptance Criteria:**

**Given** an authenticated client
**When** the developer requests available roles through `client.users`
**Then** the endpoint invokes the documented REST v1 role-list operation through the shared transport
**And** returns a typed collection of role models.

**Given** a valid role identifier
**When** the developer requests that role
**Then** the endpoint invokes the documented role lookup operation
**And** returns a typed role model with available stable role attributes.

**Given** an empty or invalid role identifier, a missing role, or malformed role data
**When** the request or response is processed
**Then** the SDK raises `ValidationError` or `NotFoundError` as appropriate
**And** no raw parser or transport failure crosses the public boundary.

### Story 4.2: Retrieve Role and User Permissions

**Requirements:** FR-16, FR-20, FR-21

As an SDK consumer,
I want to retrieve permissions assigned through a role or user,
So that automation can evaluate BCIC access using typed data.

**Acceptance Criteria:**

**Given** a valid role identifier
**When** the developer requests its permissions through `client.users`
**Then** the endpoint uses the documented `getPermissionsByRole` equivalent
**And** returns a typed collection of permission models.

**Given** a valid user identifier
**When** the developer requests that user's permissions
**Then** the endpoint uses the documented `getPermissionsByUser` equivalent
**And** returns the same typed permission model shape used for role permissions.

**Given** an invalid identifier, denied request, missing subject, or malformed permission response
**When** the operation is processed
**Then** the SDK raises `ValidationError`, `AuthorizationError`, or `NotFoundError` as appropriate
**And** public methods provide typed parameters and docstrings describing their return values.

### Story 4.3: Retrieve Binary Data

**Requirements:** FR-17, FR-20, FR-21, FR-22

As an SDK consumer,
I want to retrieve BCIC binary content and its metadata safely,
So that I can process attachments without exposing payloads through diagnostics.

**Acceptance Criteria:**

**Given** valid typed binary lookup parameters
**When** the developer retrieves content through `client.binary`
**Then** the endpoint uses the documented `getBinaryData` equivalent through the shared transport
**And** returns binary bytes or a supported stream together with typed metadata as documented.

**Given** configured buffering or streaming size constraints
**When** binary content is retrieved
**Then** the SDK follows the documented handling mode and limits
**And** rejects unsupported or unsafe sizes with a typed validation or API exception.

**Given** binary retrieval succeeds or fails
**When** operational events and exceptions are emitted
**Then** binary payload contents are never included
**And** missing data, permission failures, and malformed metadata map to appropriate SDK exceptions.

### Story 4.4: Upload Binary Data

**Requirements:** FR-17, FR-20, FR-21, FR-22

As an SDK consumer,
I want to upload binary content with typed metadata,
So that I can attach content through the SDK without constructing raw REST payloads.

**Acceptance Criteria:**

**Given** valid binary metadata and supported bytes or stream input
**When** the developer uploads content through `client.binary`
**Then** the endpoint uses the documented `setBinaryData` equivalent through the shared transport
**And** returns a typed upload result or binary metadata model.

**Given** empty content where unsupported, invalid metadata, an unsupported input type, or a known size-limit violation
**When** local validation runs
**Then** the SDK raises `ValidationError` before network execution where practical
**And** no partial upload is initiated.

**Given** BCIC rejects or fails the upload
**When** the failure is mapped
**Then** the SDK raises the corresponding validation, authorization, rate-limit, or API exception
**And** binary contents, credentials, tokens, and session identifiers are excluded from logs and exception messages.

### Story 4.5: Enforce Safe Operational Logging

**Requirements:** FR-22

As an SDK consumer,
I want useful but sanitized SDK logging,
So that I can diagnose operations without exposing credentials, sessions, or binary content.

**Acceptance Criteria:**

**Given** any SDK module emits an operational event
**When** logging is performed
**Then** it uses a module-level logger created with `logging.getLogger(__name__)`
**And** library code does not use `print()` or configure the consuming application's global logging policy.

**Given** the consuming application selects a logging level
**When** SDK operations execute
**Then** emitted event detail follows standard Python logging-level behavior
**And** useful method lifecycle, retry, and failure context is available at appropriate levels.

**Given** configuration, authentication, user, permission, or binary operations contain sensitive values
**When** log records or SDK exceptions are produced
**Then** credentials, tokens, session identifiers, and binary payloads are consistently redacted or omitted
**And** automated tests verify that representative sensitive values do not appear in captured logs or exception text.

## Epic 5: SDK Adoption, Maintainability, and Release Confidence

Maintainers and consumers can trust, learn, and extend the SDK through mockable tests, redacted operational logging, quality gates, documentation, examples, and public method docstrings.

### Story 5.1: Establish Mockable Unit-Test Infrastructure

**Requirements:** FR-23

As an SDK maintainer,
I want deterministic test infrastructure with injectable HTTP behavior,
So that SDK behavior can be verified without live BCIC credentials or tenants.

**Acceptance Criteria:**

**Given** a unit test needs to exercise an HTTP-dependent SDK component
**When** the component is constructed
**Then** the test can inject an `httpx` client, mock transport, or equivalent test adapter
**And** production defaults remain available without requiring test-specific public APIs.

**Given** representative BCIC success and failure scenarios
**When** maintainers write unit tests
**Then** reusable fixtures or builders provide sanitized request and response data
**And** tests can inspect emitted requests deterministically.

**Given** the unit-test suite executes in an environment without BCIC credentials or network access
**When** all unit tests run
**Then** they complete without contacting a live tenant
**And** accidental live HTTP execution fails clearly.

### Story 5.2: Cover Public SDK Behavior

**Requirements:** FR-22, FR-23

As an SDK maintainer,
I want focused unit coverage for public behavior and critical internal boundaries,
So that regressions are detected before release.

**Acceptance Criteria:**

**Given** the implemented SDK capabilities
**When** the unit-test suite runs
**Then** it covers configuration, authentication, transport, parsing, retries, exception mapping, pagination, models, and endpoint methods
**And** each area includes representative success and failure paths.

**Given** boundary conditions such as invalid configuration, malformed responses, exhausted retries, page limits, missing resources, denied requests, and binary size violations
**When** tests exercise them
**Then** the documented SDK result or exception is asserted
**And** raw dependency exceptions are not accepted as public outcomes.

**Given** representative credentials, tokens, session identifiers, and binary payloads
**When** tests capture logs and exception text
**Then** none of those sensitive values appear
**And** sanitized operational context remains available for diagnosis.

### Story 5.3: Enforce Automated Quality Gates

**Requirements:** FR-23, NFR-7, NFR-8, NFR-17, NFR-18, NFR-20

As an SDK maintainer,
I want reproducible automated checks for tests, style, and typing,
So that every releasable change meets the same baseline quality standard.

**Acceptance Criteria:**

**Given** a clean development or CI environment
**When** project dependencies are installed through Poetry
**Then** versions resolve reproducibly from committed `pyproject.toml` and `poetry.lock`
**And** runtime and development dependencies remain in their appropriate groups.

**Given** a proposed code change
**When** the quality workflow runs
**Then** pytest, Ruff formatting and linting, and mypy execute using configuration centralized in `pyproject.toml` where practical
**And** any failing check causes the workflow to fail.

**Given** a request to add a dependency
**When** it is reviewed
**Then** it has a documented SDK-level purpose
**And** convenience-only dependencies are not added.

### Story 5.4: Publish Consumer Documentation

**Requirements:** FR-24

As an SDK consumer,
I want task-oriented documentation for installation and common workflows,
So that I can adopt the SDK without reading its internal implementation.

**Acceptance Criteria:**

**Given** a new consumer visits the project documentation
**When** they follow the installation and quick-start guides
**Then** they can install the package, configure authentication, construct `Client`, and execute a representative high-level request
**And** examples contain placeholders rather than live secrets.

**Given** a consumer needs operational guidance
**When** they consult the documentation
**Then** authentication, error handling, pagination, and API reference material is available
**And** examples use the current public models, exceptions, and method signatures.

**Given** both domain endpoint methods and `client.methods` are documented
**When** their intended use is described
**Then** domain endpoints are presented as the preferred interface
**And** generic method access is clearly identified as a controlled lower-level escape hatch.

### Story 5.5: Provide Examples and Public API Docstrings

**Requirements:** FR-24

As an SDK consumer,
I want runnable examples and complete public method docstrings,
So that I can understand specific operations directly from code and project resources.

**Acceptance Criteria:**

**Given** the project's supported common workflows
**When** a consumer browses `examples/`
**Then** examples cover representative authentication, records, pagination, permissions, binary handling, and error handling
**And** they use environment configuration or obvious placeholders instead of embedded secrets.

**Given** any public class or method
**When** a developer inspects its docstring
**Then** the purpose, parameters, return type, and relevant raised SDK exceptions are described
**And** the description matches the implemented typed signature.

**Given** documentation or example validation runs
**When** public APIs change
**Then** stale imports and unsupported method signatures are detected where practical
**And** examples remain outside library runtime code.

### Story 5.6: Define Release and Compatibility Governance

**Requirements:** NFR-22, NFR-23

As an SDK maintainer,
I want documented versioning, release-note, and deprecation rules,
So that consumers can assess the compatibility risk of an upgrade.

**Acceptance Criteria:**

**Given** a public API change before version 1.0
**When** a release containing the change is prepared
**Then** the change is permitted under the documented pre-1.0 policy
**And** its consumer impact is recorded in release notes.

**Given** a breaking change to public endpoint methods, models, or exception names after version 1.0
**When** the release version is selected
**Then** semantic versioning requires a major version increment
**And** the breaking behavior and migration guidance are documented.

**Given** a public method is scheduled for removal after version 1.0
**When** consumers use it during the required transition period
**Then** it emits a documented deprecation warning for at least one minor release
**And** release notes identify its supported replacement and planned removal.
