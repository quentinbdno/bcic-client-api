# Story 3.5: Update Records

Status: ready-for-dev

## Story

As an SDK consumer,
I want to update selected fields on an existing BCIC record,
so that I can change record data without replacing unrelated fields or constructing REST parameters.

## Acceptance Criteria

1. `client.records.update(object_name, record_id, changes, *, use_ids=False)` validates input and POSTs `updateRecord` through the shared authenticated transport.
2. The request sends only protocol parameters plus the supplied field changes; it never retrieves, merges, or resends unrelated record fields.
3. Success returns a typed update result identifying the requested record and operation status; it does not claim to contain the updated record because the documented API returns only status/message.
4. Empty/invalid changes fail before network execution; missing, denied, or invalid updates map to `NotFoundError`, `AuthorizationError`, or `ValidationError` with sanitized context.

## Tasks / Subtasks

- [ ] Define immutable `UpdateRecordRequest` and `RecordUpdateResult` (AC: 1-4)
  - [ ] Require trimmed object/record identifiers and a non-empty JSON-compatible change mapping
  - [ ] Reject reserved protocol keys case-insensitively and preserve only explicitly supplied changes
- [ ] Implement `RecordsEndpoint.update()` through `updateRecord` POST (AC: 1-4)
  - [ ] Map `object_name`→`objName`, `record_id`→`id`, `use_ids`→`useIds`, add output, then flatten changes
  - [ ] Normalize status/message without echoing request fields or fabricating a returned record
- [ ] Add tests and run all quality gates (AC: 1-4)
  - [ ] Cover exact minimal payload, single/multiple changes, invalid input with no network, malformed success, and mapped failures
  - [ ] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Official `updateRecord` supports PUT or POST; use POST because current transport supports GET/POST and POST avoids broadening transport solely for this method.
- The documented response is standard success/failure (`status`, optional `Msg`), not record data. A typed result should use stable SDK field names while retaining sanitized message text only if safe.
- Reuse the reserved-key and dynamic-field validators from Story 3.4; do not duplicate them.
- Unknown BCIC field names may be ignored server-side. Do not claim local schema validation without metadata.
- Never include the change mapping in exception messages or logs.

### Architecture Compliance

- AD-1/AD-2: domain operation delegates to shared transport.
- AD-4: all public failures use SDK exceptions with no payload leakage.
- AD-5: typed request/result with a deliberate dynamic mapping boundary.

### Current State and Preservation

- Story 3.4 establishes write request validation and protocol-key collision rules. Extract/reuse shared private helpers in `models/records.py`.
- Preserve Story 3.1 read behavior and Stories 3.2-3.3 pagination behavior; update must not mutate cached/local records because none are part of the public contract.

### File Structure and Testing

- UPDATE: `bcic/models/records.py`, exports, `bcic/endpoints/records.py`, record endpoint/model tests.
- No transport change is expected. If response mapping reveals a generic BCIC status gap, fix it at the transport boundary with regression tests.

### Previous Story Intelligence

- Story 3.4 returns a creation result rather than a fetched record; follow the same honest result-model pattern for update.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.5]
- [Source: architecture spine — AD-1, AD-2, AD-4, AD-5, AD-8]
- [Official REST v1 `updateRecord`](https://documentation.infiniteblue.com/platform/updateRecord.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

