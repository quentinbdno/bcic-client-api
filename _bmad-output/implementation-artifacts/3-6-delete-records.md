# Story 3.6: Delete Records

Status: ready-for-dev

## Story

As an SDK consumer,
I want to delete an identified BCIC record through a typed method,
so that I can remove records without constructing a low-level call.

## Acceptance Criteria

1. `client.records.delete(object_name, record_id)` validates both identifiers and invokes REST v1 `deleteRecord` through shared authentication, transport, parsing, and exception mapping.
2. The request sends only `objName`, `id`, and configured output; no raw URL or session ID appears in endpoint code.
3. Success returns a typed deletion result identifying the requested object/record and successful status; documentation states that normal Platform records move to the Recycle Bin while external-object behavior is server-defined.
4. Invalid local input sends no request; missing, denied, invalid, server, and malformed responses map to the corresponding sanitized SDK exception without exposing raw HTTP/BCIC structures.

## Tasks / Subtasks

- [ ] Define immutable `RecordDeletionResult` and identifier validation reuse (AC: 1-4)
  - [ ] Normalize documented status/message without inventing a hard-delete guarantee
- [ ] Implement `RecordsEndpoint.delete()` through `deleteRecord` (AC: 1-4)
  - [ ] Use documented GET support because current transport intentionally supports GET/POST only
  - [ ] Centralize method metadata and add configured JSON output
- [ ] Add tests and run all quality gates (AC: 1-4)
  - [ ] Cover exact request, typed result, invalid identifiers/no network, malformed response, and every mapped error class relevant to the AC
  - [ ] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Official `deleteRecord` supports DELETE or GET. Use GET to avoid expanding the shared `HTTPMethod` contract solely for this operation; document this intentional choice.
- The operation moves normal Platform records to the Recycle Bin and deletes external objects according to server behavior. The SDK result must say the request succeeded, not promise irreversible deletion.
- Official parameters are `objName`, `id`, `output`, plus transport-owned authentication.
- Reuse identifier validation from get/update. Do not duplicate validators or expose raw status payloads.

### Architecture Compliance

- AD-1/AD-2/AD-3: domain method, transport-owned request/session behavior.
- AD-4/AD-5: typed result and SDK-only failures.
- AD-8: deterministic mock transport coverage with no live calls.

### Current State and Preservation

- Stories 3.1-3.5 establish all record endpoint validation, method metadata, result models, and response normalization. Keep delete as a focused addition.
- Existing transport already maps HTTP 404/403/400/5xx. Preserve those mappings and retry only server/network/rate-limit failures.

### File Structure and Testing

- UPDATE: `bcic/models/records.py`, exports, `bcic/endpoints/records.py`, record endpoint/model tests.
- No new module or dependency is expected.

### Previous Story Intelligence

- Story 3.5 defines typed status-result normalization and identifier validation. Reuse both, changing only operation-specific fields and semantics.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.6]
- [Source: architecture spine — AD-1 through AD-5, AD-8]
- [Official REST v1 `deleteRecord`](https://documentation.infiniteblue.com/platform/deleteRecord.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

