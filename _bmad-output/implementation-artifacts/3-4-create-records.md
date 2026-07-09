# Story 3.4: Create Records

Status: ready-for-dev

## Story

As an SDK consumer,
I want to create a BCIC record using a typed request,
so that I can submit dynamic fields without invoking a generic REST method.

## Acceptance Criteria

1. `client.records.create(object_name, fields, *, use_ids=False)` validates input and POSTs `createRecord` through the shared authenticated transport.
2. The request sends `objName`, `useIds`, dynamic field integration names/values, and configured JSON output; reserved protocol keys cannot be overwritten by dynamic fields.
3. A successful response returns a documented typed creation result containing non-empty string `record_id` and `object_name`.
4. Invalid local input fails before network execution; BCIC validation failures remain sanitized SDK `ValidationError` and do not expose field payloads, credentials, or session IDs.

## Tasks / Subtasks

- [ ] Define immutable `CreateRecordRequest` and `RecordCreationResult` models (AC: 1-4)
  - [ ] Require trimmed object name and a non-empty JSON-compatible field mapping with valid non-empty string keys
  - [ ] Reject reserved keys (`objName`, `id`, `useIds`, `output`, `sessionId`) case-insensitively
- [ ] Implement `RecordsEndpoint.create()` through `createRecord` (AC: 1-4)
  - [ ] Flatten validated dynamic fields into documented POST parameters without logging/embedding the payload in errors
  - [ ] Normalize documented `id`/`objName` response keys into the typed result
- [ ] Add tests and run all quality gates (AC: 1-4)
  - [ ] Cover exact POST JSON, success result, empty/invalid/reserved fields, malformed response, and mapped BCIC validation/authorization failures
  - [ ] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Official `createRecord` is POST; it returns the new ID and object name, not a complete record. Return a typed creation result rather than issuing an undocumented follow-up GET.
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
- Assert local validation leaves the mock request list empty and exception text excludes representative secret/field values.

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

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

