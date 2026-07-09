# Story 4.1: Retrieve Roles

Status: ready-for-dev

## Story

As an SDK consumer,
I want to retrieve BCIC roles through typed high-level methods,
so that I can inspect authorization structures without constructing generic REST calls.

## Acceptance Criteria

1. `client.users.list_roles()` invokes REST v1 `getRoles` through the shared authenticated transport and returns `list[Role]`.
2. `client.users.get_role(role_id)` validates a non-empty role original ID, invokes `getRoleById`, and returns one `Role`.
3. `Role` preserves the documented name, nullable integration code/description, ID, and original ID using stable snake-case SDK fields.
4. Invalid identifiers fail before network execution; missing or malformed role data raises sanitized `NotFoundError` or `ValidationError`; permission and transport failures remain mapped SDK exceptions.

## Tasks / Subtasks

- [ ] Define the immutable `Role` response model and normalization (AC: 1-4)
  - [ ] Normalize `originalId` to `original_id`; require non-empty name, ID, and original ID while preserving nullable/empty optional text
  - [ ] Validate role lists atomically and reject malformed top-level/item shapes without partial results
- [ ] Implement role methods on `UsersEndpoint` (AC: 1-4)
  - [ ] Centralize `getRoles` and `getRoleById` in endpoint method metadata
  - [ ] Send configured JSON output and `roleId` only where required; keep authentication transport-owned
- [ ] Add unit tests and run all quality gates (AC: 1-4)
  - [ ] Cover list/single request shapes, empty lists, identifier validation, malformed data, not found, authorization, and parser failures
  - [ ] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Create `bcic/models/users.py`; use existing strict frozen `SDKModel`.
- Official `getRoles` and `getRoleById` are GET and require full administrative privileges. `getRoleById.roleId` is the role's original ID, not its tenant-local `id`; make this explicit in docstrings.
- `getRoles` omits Super Admin; `getRoleById` rejects Super Admin. Do not locally fabricate or special-case unseen roles.
- Official JSON for `getRoles` is a top-level array, while the current `ResponseParser` only accepts mappings. Extend the transport/parser result type deliberately for JSON arrays and preserve existing mapping callers and BCIC-status handling.
- Add no dependency and do not route high-level methods through `MethodsEndpoint`.

### Architecture Compliance

- AD-1/AD-2: domain-first methods provide REST method metadata and parameters; transport builds requests.
- AD-3/AD-4: no session values in endpoint code; only sanitized SDK failures escape.
- AD-5/AD-8/AD-10: typed Pydantic returns, mock HTTP tests, JSON-first parser boundary.

### Current State and Preservation

- `UsersEndpoint` is an empty composed endpoint; preserve the shared `_EndpointContext`.
- `RestTransport.execute()` owns URL construction, authentication, retry, parsing, and exception mapping. Array support must not weaken malformed JSON checks or bypass status mapping for mapping responses.
- Existing public models are exported from `bcic/models/__init__.py`; follow that pattern.

### File Structure and Testing

- NEW: `bcic/models/users.py`, `tests/unit/test_endpoints_users.py`.
- UPDATE: `bcic/models/__init__.py`, `bcic/endpoints/users.py`, and `bcic/transport.py` as required for top-level JSON arrays.
- Use `httpx.MockTransport`; assert no live calls and no request for invalid local input.

### Previous Story and Git Intelligence

- Epic 3 story specifications established typed normalization at endpoint/model boundaries, but Epic 3 implementation is not yet present. Build only on committed runtime behavior from Epic 2.
- Recent commit `fae53d5` added story context only; current source remains the Epic 2 implementation baseline.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 4, Story 4.1]
- [Source: architecture spine — AD-1 through AD-5, AD-8, AD-10]
- [Source: PRD — FR-16, FR-20, FR-21]
- [Official REST v1 `getRoles`](https://documentation.infiniteblue.com/platform/getRoles.htm)
- [Official REST v1 `getRoleById`](https://documentation.infiniteblue.com/platform/getRoleById.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

