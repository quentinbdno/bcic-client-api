---
baseline_commit: 34f7e1fe4e572f92b219073dd796bb200da563d1
---

# Story 3.4: Create Records

Status: review

## Story

As an SDK consumer,
I want to create a BCIC record using a typed request,
so that I can submit dynamic fields without invoking a generic REST method.

## Acceptance Criteria

1. `client.records.create(object_name, fields, *, use_ids=False)` validates input and POSTs `createRecord` through the shared authenticated transport.
2. The request sends `objName`, `useIds`, dynamic field integration names/values, and configured JSON output; reserved protocol keys cannot be overwritten by dynamic fields.
3. A successful response returns a documented typed creation result containing non-empty string `record_id` and `object_name`; a returned `objName` that does not match the requested object name is treated as a malformed response and raises sanitized SDK `ValidationError`.
4. Invalid local input fails before network execution; BCIC validation failures remain sanitized SDK `ValidationError` and do not expose field payloads, credentials, or session IDs.

## Tasks / Subtasks

- [x] Define immutable `CreateRecordRequest` and `RecordCreationResult` models (AC: 1-4)
  - [x] Require trimmed object name and a non-empty JSON-compatible field mapping with valid non-empty string keys
  - [x] Reject reserved keys (`objName`, `id`, `useIds`, `output`, `sessionId`) case-insensitively
- [x] Implement `RecordsEndpoint.create()` through `createRecord` (AC: 1-4)
  - [x] Flatten validated dynamic fields into documented POST parameters without logging/embedding the payload in errors
  - [x] Normalize documented `id`/`objName` response keys into the typed result and reject returned object-name mismatches
- [x] Add tests and run all quality gates (AC: 1-4)
  - [x] Cover exact POST JSON, success result, empty/invalid/reserved fields, malformed response, and mapped BCIC validation/authorization failures
  - [x] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Official `createRecord` is POST; it returns the new ID and object name, not a complete record. Return a typed creation result rather than issuing an undocumented follow-up GET. Compare the returned object name to the requested object name after normalizing surrounding whitespace; do not silently trust mismatched identity.
- Field values use BCIC CSV-import semantics and relationships may use pipe-separated IDs. Keep values within the deliberate `JSONValue` boundary; do not invent tenant-specific coercion.
- The official API may ignore unknown field names. Local validation can reject structural errors but must not claim schema validation without metadata.
- `useIds` controls lookup/picklist interpretation. Keep its Python spelling `use_ids` and transport spelling `useIds`.
- Add no logging of request fields and no new dependency.

### Architecture Compliance

- AD-1/AD-2: high-level record operation, transport-owned HTTP construction.
- AD-3/AD-4: session attachment and sanitized error mapping remain shared.
- AD-5: request/result are Pydantic models; dynamic fields stay explicitly bounded.

### Current State and Preservation

- Reuse record input validators/normalizers established in Stories 3.1-3.2.
- `RestTransport.execute()` already supports POST JSON and mapped validation/authorization errors. Preserve retry policy: validation and permission failures are not retried.

### File Structure and Testing

- UPDATE: `bcic/models/records.py`, `bcic/models/__init__.py`, `bcic/endpoints/records.py`.
- UPDATE: `tests/unit/test_endpoints_records.py` and model tests as needed.
- Assert local validation leaves the mock request list empty, response object-name mismatches raise `ValidationError`, and exception text excludes representative secret/field values.

### Previous Story Intelligence

- Stories 3.1-3.3 define record naming, JSON value, and endpoint patterns. Reuse them; creation does not belong in pagination.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.4]
- [Source: architecture spine — AD-1 through AD-5, AD-8]
- [Official REST v1 `createRecord`](https://documentation.infiniteblue.com/platform/createRecord.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-07-09: Implemented sanitized dynamic-field validation and create request/result flow.

### Implementation Plan

- Validate immutable write input before transport, flatten only approved fields, and normalize the documented creation identity.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added immutable create request/result models and case-insensitive protocol-key protection.
- Added exact POST payload, local rejection, result, and failure coverage.
- Validated with 98 passing tests, Ruff format/check, and strict mypy.

### File List

- bcic/endpoints/records.py
- bcic/models/__init__.py
- bcic/models/records.py
- tests/unit/test_endpoints_records.py

## Change Log

- 2026-07-09: Added typed record creation.
