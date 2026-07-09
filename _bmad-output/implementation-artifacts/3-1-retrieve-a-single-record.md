# Story 3.1: Retrieve a Single Record

Status: ready-for-dev

## Story

As an SDK consumer,
I want to retrieve one BCIC record by object name and identifier,
so that I can use record data without calling a generic REST method or parsing a raw response.

## Acceptance Criteria

1. `client.records.get(object_name, record_id, *, field_names=None, composite=0)` validates its inputs, calls REST v1 `getRecord` through the shared transport, and does not expose URLs or session parameters.
2. A successful JSON response is normalized into `DynamicRecord`, preserving `object_name`, string `record_id`, and JSON-compatible dynamic fields.
3. Empty identifiers, invalid composite depth, malformed responses, and response identity mismatches raise sanitized SDK `ValidationError`; missing records raise `NotFoundError`; raw Pydantic, parser, and transport errors do not cross the public boundary.
4. The public method is fully typed and documents parameters, return value, and relevant SDK exceptions.

## Tasks / Subtasks

- [ ] Define record response normalization at the model boundary (AC: 2, 3)
  - [ ] Accept documented JSON record keys (`objName`, `id`) and separate remaining field values into `fields`
  - [ ] Reject missing/empty identity, non-mapping data, non-JSON field values, and requested/returned identity mismatches
- [ ] Implement `RecordsEndpoint.get()` using shared transport (AC: 1, 3, 4)
  - [ ] Centralize `getRecord` in `REST_METHODS`; send `objNames`, `id`, `composite`, optional comma-joined `fieldList`, and configured `output`
  - [ ] Validate non-empty trimmed names/IDs, `composite >= 0`, and non-empty field names before network execution
- [ ] Add focused unit tests and run all quality gates (AC: 1-4)
  - [ ] Cover request shape, authentication reuse, normalization, input rejection without network calls, malformed payloads, identity mismatch, and mapped failures
  - [ ] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Extend `bcic/endpoints/records.py`; do not route the high-level operation through `MethodsEndpoint`.
- Extend `bcic/models/records.py` with a small normalization function or typed response model. Keep unrestricted dynamic values only at the existing `JSONValue` boundary.
- REST v1 `getRecord` is GET. Official parameters are `id`, optional `objNames`, `composite` (default 0), `fieldList`, and `output`; authentication remains transport-owned.
- The documented JSON shape may be tenant/version-sensitive. Normalize only explicitly supported mapping shapes and reject ambiguity; never invent identity from request data when the response contradicts it.
- Reuse `RestTransport.execute()` and existing exception mapping. Add no dependency and do not modify authentication or URL construction.

### Architecture Compliance

- AD-1/AD-2: domain-first method; endpoint supplies method metadata and typed parameters only.
- AD-3/AD-4: no session handling in the endpoint; only SDK exceptions escape.
- AD-5: return the existing immutable `DynamicRecord`.
- AD-8/AD-10: mock HTTP in unit tests and request JSON output through the parser boundary.

### Current State and Preservation

- `RecordsEndpoint` is empty; preserve its shared `_EndpointContext`.
- `RestTransport.execute()` accepts GET/POST JSON mappings, adds authentication, retries mapped transient failures, parses mappings, and maps status failures. Do not duplicate these behaviors.
- `DynamicRecord` already enforces non-empty identity and recursive JSON-compatible fields. Preserve strict/frozen model behavior and existing exports.

### File Structure and Testing

- UPDATE: `bcic/endpoints/records.py`, `bcic/models/records.py`, `bcic/models/__init__.py` only if a new public type is added.
- NEW: `tests/unit/test_endpoints_records.py` (preferred over expanding the endpoint-composition test).
- Tests must use `httpx.MockTransport`, require no credentials/tenant, and assert no request occurs for locally invalid input.

### Previous Story and Git Intelligence

- Epic 2 established shared transport execution and recursive JSON parameter validation. Reuse those patterns; `3ea7230` is the current Epic 2 baseline.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.1]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-bcic-client-api-2026-07-08/ARCHITECTURE-SPINE.md` — AD-1 through AD-5, AD-8, AD-10]
- [Source: `_bmad-output/planning-artifacts/prds/prd-bcic-client-api-2026-07-08/prd.md` — FR-14, FR-20, FR-21]
- [Official REST v1 `getRecord`](https://documentation.infiniteblue.com/platform/getRecord.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

