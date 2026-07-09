---
baseline_commit: b1f383f1fc11ad0e3d50214a46df2b647f37a06d
---

# Story 4.4: Upload Binary Data

Status: review

## Story

As an SDK consumer,
I want to upload binary content with typed metadata,
so that I can attach content without constructing raw REST payloads.

## Acceptance Criteria

1. `client.binary.set(object_name, record_id, field_name, content, *, file_name, content_type, max_bytes=10_485_760)` validates metadata, bytes-like input, non-empty content, and the positive size limit before network execution.
2. The endpoint Base64-encodes the validated bytes and POSTs documented `setBinaryData` parameters through shared authentication/transport; payload contents are never logged or embedded in exceptions.
3. Success returns immutable `BinaryUploadResult` containing object/record/field identity and normalized status/message without retaining or echoing content.
4. Unsupported input, oversize content, malformed success, and BCIC validation/authorization/rate-limit/server failures map to sanitized SDK exceptions; no partial upload is initiated after local failure.

## Tasks / Subtasks

- [x] Define upload request validation and result model (AC: 1-4)
  - [x] Accept `bytes`, `bytearray`, and read-only `memoryview` by converting once to immutable bytes; reject streams in MVP
  - [x] Require trimmed identifiers/file name/content type and enforce non-empty/max byte size before Base64 encoding
- [x] Implement `BinaryEndpoint.set()` through `setBinaryData` POST (AC: 1-4)
  - [x] Send `objName`, `id`, `fieldName`, Base64 `value`, `contentType`, `fileName`, and `output=json`
  - [x] Normalize only status/message into a content-free typed result
- [x] Add tests and run all quality gates (AC: 1-4)
  - [x] Cover exact encoded request, accepted bytes-like types, empty/oversize/invalid inputs with no request, malformed response, mapped failures, and payload absence from logs/errors/repr
  - [x] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Extend `bcic/models/binary.py` and `BinaryEndpoint`; use standard-library Base64.
- Official `setBinaryData` accepts GET or POST and Base64 `value` for file fields. Use POST through the existing transport.
- Although one official example uses multipart, the documented parameter contract explicitly accepts Base64 `value`; use the existing JSON POST boundary for MVP and test exact behavior. Do not add multipart or streaming dependencies.
- The 10 MiB decoded-content default matches Story 4.3 as an SDK safety choice, not a BCIC limit. Validate decoded input length before encoding.
- Readable streams are out of scope because safe length validation and replay semantics require a streaming transport design. Reject them explicitly rather than buffering arbitrary objects.

### Architecture Compliance

- AD-1/AD-2/AD-3: domain method uses shared transport and session strategy.
- AD-4/AD-5: typed result and sanitized public failures.
- AD-8: mock request inspection verifies encoding without live upload.
- FR-22/NFR-10: Base64 and raw bytes are sensitive payloads and must be omitted from diagnostics.

### Current State and Preservation

- Story 4.3 introduces shared binary identifier/metadata/limit validation. Reuse it and keep the same max-byte semantics.
- `RestTransport.execute()` supports JSON POST and retryable mapped failures. Do not implement upload-specific retries; replay behavior remains transport-owned for this buffered immutable request.

### File Structure and Testing

- UPDATE: `bcic/models/binary.py`, exports, `bcic/endpoints/binary.py`, `tests/unit/test_endpoints_binary.py`.
- No transport or dependency change is expected.

### Previous Story Intelligence

- Story 4.3 defines payload-safe repr/error behavior. Upload results must never retain content or Base64.
- No implementation completion notes exist while 4.3 remains ready-for-dev.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 4, Story 4.4]
- [Source: architecture spine — AD-1 through AD-5, AD-8]
- [Official REST v1 `setBinaryData`](https://documentation.infiniteblue.com/platform/setBinaryData.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Binary upload bytes-like, exact body, invalid input, and malformed response tests passed.
- Full suite and static quality gates passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added validated Base64 upload for supported immutable-convertible bytes-like inputs.
- Added content-free immutable upload results and payload-safety coverage.

### File List

- bcic/endpoints/binary.py
- bcic/models/__init__.py
- bcic/models/binary.py
- tests/unit/test_endpoints.py
- tests/unit/test_endpoints_binary.py

### Change Log

- 2026-07-09: Implemented bounded binary upload; status set to review.
