# BCIC Client API - REST v2 Readiness Backlog

Date: 2026-07-29
Owner: SDK Team
Status: Ready for sprint planning

## Objective

Deliver REST v2 support in the existing SDK without breaking REST v1 behavior.

## Scope Definition

In scope:
- Explicit version selection in one package.
- Dedicated REST v2 transport/auth/endpoints/models.
- Compatibility and regression protection for v1.
- Updated docs, examples, and release notes.

Out of scope for first release:
- Full parity with every REST v2 admin/system endpoint.
- Auto-detection of API version.
- Removal of any v1 public API.

## Milestones

- M1 Foundation: Epics 1-2 complete.
- M2 Core v2 Runtime: Epics 3-4 complete.
- M3 Quality and Adoption: Epics 5-6 complete.

## Epic Overview

| Epic | Priority | Outcome |
| --- | --- | --- |
| E1 | P0 | Versioned architecture boundary in one SDK |
| E2 | P0 | REST v2 transport and auth foundation |
| E3 | P0 | Core v2 record/custom/user endpoints |
| E4 | P1 | v2 model and pagination normalization |
| E5 | P0 | Test and compatibility safety net |
| E6 | P1 | Documentation, examples, and release readiness |

---

## E1 - Versioned SDK Boundary (P0)

Goal: Keep one package while enforcing clear v1/v2 isolation.

### Story E1-S1: Introduce a version-aware internal wiring layer
Description:
- Add a factory/composition layer that resolves v1 or v2 adapters from api_version.

Acceptance criteria:
- Client initialization with api_version=v1 uses existing v1 adapters.
- Client initialization with api_version=v2 uses v2 adapters.
- No endpoint module contains mixed v1/v2 branching logic.

Dependencies:
- None

### Story E1-S2: Preserve public client contract
Description:
- Keep current constructor defaults and v1 default behavior stable.

Acceptance criteria:
- Existing v1 usage patterns run unchanged.
- api_version defaults to v1.
- No breaking changes to current public endpoint property names.

Dependencies:
- E1-S1

### Story E1-S3: Define package/module layout for versioned adapters
Description:
- Add version-specific internal modules for transport/auth/endpoints/models.

Acceptance criteria:
- v1 and v2 internals are physically separated.
- Shared primitives stay in common modules.
- A maintainer can identify the version boundary within 5 minutes.

Dependencies:
- E1-S1

---

## E2 - REST v2 Transport and Authentication (P0)

Goal: Implement correct v2 routing and auth semantics based on official docs.

### Story E2-S1: Build v2 path and method router
Description:
- Implement a v2 transport that supports resource-style routes and required HTTP verbs.

Acceptance criteria:
- Supports GET, POST, PUT, DELETE.
- Uses documented v2 paths for user, custom, data, meta, and system resources.
- Stops using v1-style method routing for v2.

Dependencies:
- E1-S1

### Story E2-S2: Implement v2 auth strategy (JWT/API-key)
Description:
- Create v2 auth flow with user login/logout and token/header handling.

Acceptance criteria:
- Login flow returns and stores JWT or equivalent token state.
- Auth headers are injected by v2 auth strategy, not endpoint code.
- Logout invalidates v2 auth state and behaves idempotently.

Dependencies:
- E2-S1

### Story E2-S3: Add v2 status/envelope/error mapping
Description:
- Map v2 HTTP/envelope failures to shared SDK exception hierarchy.

Acceptance criteria:
- 4xx/5xx and envelope failures map to typed SDK exceptions.
- No credentials or tokens leak in logs/exceptions.
- Retry policy excludes auth/validation failures by default.

Dependencies:
- E2-S1

---

## E3 - Core v2 Endpoints (P0)

Goal: Provide first usable v2 functional surface for automation.

### Story E3-S1: v2 custom methods endpoint
Description:
- Implement custom method operations for GET/POST/PUT/DELETE on documented v2 custom route.

Acceptance criteria:
- Method executor targets v2 custom resource paths.
- Query/body handling matches HTTP method rules.
- Validation blocks path injection and invalid method names.

Dependencies:
- E2-S1, E2-S2

### Story E3-S2: v2 records read operations
Description:
- Implement single record, collection page, and count operations for v2 data routes.

Acceptance criteria:
- Retrieve one record by objectIntegrationName and recordId.
- Retrieve paged records with start/count and optional filters.
- Return normalized typed page structure.

Dependencies:
- E2-S1, E2-S3

### Story E3-S3: v2 records write operations
Description:
- Implement create, update, and delete for single and batch paths in v2.

Acceptance criteria:
- Create, update, delete map to documented endpoints and verbs.
- Request validation catches obvious invalid IDs and field maps.
- Returns normalized operation results.

Dependencies:
- E3-S2

### Story E3-S4: v2 users core operations
Description:
- Implement list/get/update/delete user operations for the v2 users surface.

Acceptance criteria:
- List and get user operations function via v2 routes.
- Update and delete operations use proper v2 paths/verbs.
- Permission/auth failures map to typed exceptions.

Dependencies:
- E2-S1, E2-S3

---

## E4 - v2 Models and Pagination Semantics (P1)

Goal: Ensure v2 responses are strongly typed without distorting contract details.

### Story E4-S1: Add v2 envelope models
Description:
- Create typed models for v2 code/message/results envelopes and variants.

Acceptance criteria:
- Supports object and list-style results payloads.
- Validation errors convert to SDK ValidationError at API boundary.
- Model module is separated from v1 models.

Dependencies:
- E2-S3

### Story E4-S2: Implement v2 page metadata normalization
Description:
- Normalize start/count behavior and has_more derivation for v2 responses.

Acceptance criteria:
- Page metadata includes start_row, page_size, returned_count.
- has_more and total_items are correct when present or derivable.
- list_all traversal guardrails remain configurable.

Dependencies:
- E3-S2

### Story E4-S3: Align binary and advanced field handling for v2
Description:
- Add support for v2 advanced field read/update patterns where needed.

Acceptance criteria:
- Binary/advanced fields follow documented v2 request format.
- Payload size limits and redaction policies are enforced.
- Typed result models return metadata without exposing raw sensitive content.

Dependencies:
- E2-S1, E4-S1

---

## E5 - Compatibility and Test Safety Net (P0)

Goal: Prevent regressions while adding v2 capability.

### Story E5-S1: Lock v1 compatibility contract tests
Description:
- Add/expand v1 regression tests for auth, transport paths, and endpoint behavior.

Acceptance criteria:
- Existing v1 tests remain green.
- Additional tests cover constructor defaults and v1 endpoint URLs.
- CI blocks merges on v1 regressions.

Dependencies:
- E1-S2

### Story E5-S2: Add v2 transport/auth contract tests
Description:
- Add route, header, verb, retry, and exception mapping tests for v2.

Acceptance criteria:
- Tests assert documented v2 path patterns.
- Tests verify JWT/API-key header behavior.
- Tests verify no token leakage in logs/errors.

Dependencies:
- E2-S1, E2-S2, E2-S3

### Story E5-S3: Add dual-version endpoint behavior tests
Description:
- Validate v1 and v2 endpoint behaviors are isolated and correct.

Acceptance criteria:
- Same high-level call intent can be tested for both versions with expected differences.
- No mixed version route assertions in a single adapter.
- Coverage includes records + custom methods + one user path.

Dependencies:
- E3-S1, E3-S2, E3-S4

---

## E6 - Docs, Examples, and Release Governance (P1)

Goal: Make adoption and maintenance clear and low-risk.

### Story E6-S1: Publish v1 vs v2 usage guidance
Description:
- Document version selection, auth differences, and endpoint availability matrix.

Acceptance criteria:
- Docs clearly show when to choose v1 vs v2.
- Version selection examples cover constructor and environment variable usage.
- Unsupported/partial v2 areas are clearly marked.

Dependencies:
- E1-S2, E3-S2

### Story E6-S2: Add runnable examples for v2
Description:
- Add focused examples for v2 login, record read, and custom method call.

Acceptance criteria:
- Examples run with documented environment variables.
- Examples avoid secrets in source.
- Examples include expected response-shape notes.

Dependencies:
- E2-S2, E3-S1, E3-S2

### Story E6-S3: Release and migration checklist
Description:
- Add release checklist covering compatibility evidence, docs updates, and changelog guidance.

Acceptance criteria:
- Checklist includes v1 regression suite proof.
- Changelog template includes migration guidance section.
- Versioning policy references dual-version support expectations.

Dependencies:
- E5-S1, E5-S2

---

## Cross-Epic Definition of Done

- Unit tests for changed behavior are added and passing.
- No sensitive auth data appears in logs or exception messages.
- Public API changes are documented.
- Type checks and lint checks pass.
- v1 compatibility is validated before merge.

## Suggested Sprint Slices

Sprint A (highest risk first): E1 + E2
- Outcome: isolated v2 engine in place.

Sprint B (first user value): E3-S1, E3-S2, E5-S2
- Outcome: usable v2 custom and read-path with confidence tests.

Sprint C (functional completion): E3-S3, E3-S4, E4-S2, E5-S3
- Outcome: core CRUD plus user operations and isolation coverage.

Sprint D (hardening and adoption): E4-S1, E4-S3, E6
- Outcome: typed polishing, binary alignment, docs, release readiness.
