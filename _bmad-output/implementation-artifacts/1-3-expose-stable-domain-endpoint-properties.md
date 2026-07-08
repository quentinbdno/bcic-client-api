---
baseline_commit: 735639e6fedc09bcbbf016cecf1cfc1898558cfa
---

# Story 1.3: Expose Stable Domain Endpoint Properties

Status: review

## Story

As an SDK consumer,
I want stable endpoint properties on the client,
so that I can discover and use BCIC capabilities without depending on internal modules or transport details.

## Acceptance Criteria

1. **Given** a configured `Client`  
   **When** the developer accesses its public domain properties  
   **Then** `client.records`, `client.users`, `client.binary`, and `client.methods` are available  
   **And** each property returns the corresponding endpoint object.

2. **Given** any endpoint object exposed by the client  
   **When** it is created or reused  
   **Then** it receives shared configuration, transport, authentication, and parsing dependencies through composition  
   **And** the public API does not expose raw URLs, `httpx` clients, or BCIC session identifiers.

3. **Given** a new endpoint domain is added later  
   **When** it is integrated into the client  
   **Then** existing endpoint implementations do not require modification  
   **And** BCIC method names remain centralized in constants or endpoint metadata rather than duplicated across request logic.

## Tasks / Subtasks

- [x] Establish the endpoint composition boundary (AC: 2, 3)
  - [x] Add `bcic/endpoints/base.py` with a private shared context and typed base endpoint.
  - [x] Add configuration-bound transport, authentication, and parser dependency
    descriptors that Epic 2 can extend with behavior.
  - [x] Do not create fake network/auth/parser implementations or expose the context publicly.
- [x] Add the four stable endpoint types (AC: 1, 3)
  - [x] Add cohesive records, users, binary, and methods modules and package exports.
  - [x] Give each module a centralized `REST_METHODS` metadata tuple for later method promotion; do not invent method behavior now.
- [x] Compose and cache endpoint properties on `Client` (AC: 1, 2)
  - [x] Create one shared context per client and one endpoint instance per domain.
  - [x] Add documented read-only properties without changing the top-level `bcic.__all__`.
- [x] Test and validate the endpoint foundation (AC: 1–3)
  - [x] Assert types, stable identity, shared private context, public non-exposure, and module independence.
  - [x] Run the complete pytest, Ruff, mypy, and Poetry checks.

## Dev Notes

### Developer Context and Guardrails

- Preserve Story 1.2 configuration behavior and sanitization.
- This story creates object topology, not HTTP behavior. Authentication, session state, parser, retry, and transport implementations belong to Epic 2.
- The shared context is the extension seam: later stories add adapters there without changing individual endpoint constructors.
- Repeated property access must return the same endpoint object.
- Do not place REST method strings in `Client` or base classes. Empty per-domain metadata is valid until a story defines supported methods.

### Architecture Compliance

- Follow AD-1 and AD-2. Add `bcic/endpoints/{__init__,base,records,users,binary,methods}.py`; update `bcic/client.py`; add `tests/unit/test_endpoints.py`.
- Endpoint types are not added to top-level `bcic.__all__`.
- Do not add dependencies or modify package metadata.

### Previous Story Intelligence

- `Client.config` is immutable and validated; direct and environment constructors converge on the same initializer.
- The complete suite currently has 14 passing tests and strict Ruff/mypy gates.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 1, Story 1.3]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-bcic-client-api-2026-07-08/ARCHITECTURE-SPINE.md` — AD-1, AD-2, AD-3, Capability Map]
- [Source: `_bmad-output/planning-artifacts/prds/prd-bcic-client-api-2026-07-08/prd.md` — FR-3, NFR-1, NFR-2]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- RED: endpoint tests failed during collection because `bcic.endpoints` did not exist.

### Implementation Plan

- Define one private typed composition context, add independent endpoint types,
  and cache one instance of each on `Client`.
- Verify topology and non-exposure without introducing transport behavior.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added four cached domain endpoint properties backed by one private typed
  composition context, without inventing deferred network behavior.
- Added independent endpoint modules and centralized per-domain REST metadata
  seams; all 17 tests and Poetry/Ruff/mypy checks pass.

### File List

- `bcic/client.py`
- `bcic/endpoints/__init__.py`
- `bcic/endpoints/base.py`
- `bcic/endpoints/records.py`
- `bcic/endpoints/users.py`
- `bcic/endpoints/binary.py`
- `bcic/endpoints/methods.py`
- `tests/unit/test_endpoints.py`
- `_bmad-output/implementation-artifacts/1-3-expose-stable-domain-endpoint-properties.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-07-08: Added stable cached domain endpoint properties and their shared
  private composition boundary.
