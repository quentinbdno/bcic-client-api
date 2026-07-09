---
baseline_commit: b1f383f1fc11ad0e3d50214a46df2b647f37a06d
---

# Story 4.3: Retrieve Binary Data

Status: review

## Story

As an SDK consumer,
I want to retrieve BCIC binary content and its metadata safely,
so that I can process attachments without exposing payloads through diagnostics.

## Acceptance Criteria

1. `client.binary.get(object_name, record_id, field_name, *, max_bytes=10_485_760)` validates lookup parameters and a positive buffer limit, then invokes REST v1 `getBinaryData` through shared transport/authentication.
2. MVP requests documented JSON output, strictly Base64-decodes `fileData`, enforces `max_bytes` on the decoded content, and returns immutable `BinaryData(content, metadata)`.
3. `BinaryMetadata` includes object/record/field identity, file name, content type, and decoded size; malformed Base64/metadata, empty content where unsupported, or oversized content raises sanitized `ValidationError`/`APIError`.
4. Missing and denied attachments map to SDK exceptions, and binary/Base64 contents never appear in logs, exception text, or repr output.

## Tasks / Subtasks

- [x] Define safe immutable binary models and decoding boundary (AC: 1-4)
  - [x] Add `BinaryMetadata` and `BinaryData`; exclude/restrict content representation so model repr never emits bytes
  - [x] Strictly validate the field-keyed JSON envelope, metadata strings, Base64 encoding, and decoded size
- [x] Implement bounded retrieval on `BinaryEndpoint` (AC: 1-4)
  - [x] Centralize `getBinaryData`; send `objName`, `id`, `fieldName`, and `output=json`
  - [x] Validate trimmed identifiers and positive `max_bytes` before network execution
- [x] Add safety-focused tests and run all quality gates (AC: 1-4)
  - [x] Cover success, exact/over limit, invalid Base64, mismatched field envelope, missing metadata, zero requests for invalid input, mapped failures, and absence of payload text in repr/logs/errors
  - [x] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Create `bcic/models/binary.py`; use standard-library `base64` only.
- Official `getBinaryData` supports raw, XML, and JSON. Use JSON for MVP because current parser is JSON-first and the JSON envelope provides `contentType`, `fileName`, and Base64 `fileData`.
- Buffering is the documented MVP behavior. The 10 MiB default is an SDK safety limit, not a claimed BCIC server limit; callers may lower/raise it explicitly. Raw streaming is deferred until the transport supports streaming without routing bytes through the JSON parser.
- Preflight Base64 encoded length before decoding to avoid obviously oversized allocations, then enforce the authoritative decoded byte count. Use strict decoding (`validate=True`).
- Binary content must not be stored in generic JSON mappings longer than necessary or included in validation diagnostics.

### Architecture Compliance

- AD-1/AD-2/AD-3: binary domain endpoint delegates request/auth behavior.
- AD-4: parser/decode failures become sanitized SDK errors.
- AD-5/AD-8/AD-10: typed metadata/result, mock tests, JSON-first parser boundary.
- FR-22/NFR-10: never log or render binary payloads.

### Current State and Preservation

- `BinaryEndpoint` is empty and shares `_EndpointContext`; preserve composition.
- Current `ResponseParser` returns JSON mappings, which fits JSON binary envelopes. Do not add raw response access to endpoints.
- Story 4.1 may broaden transport JSON types for arrays; binary retrieval remains mapping-only and should narrow/validate explicitly.

### File Structure and Testing

- NEW: `bcic/models/binary.py`, `tests/unit/test_endpoints_binary.py`.
- UPDATE: `bcic/models/__init__.py`, `bcic/endpoints/binary.py`.
- No dependency or transport API expansion is expected for buffered JSON mode.

### Previous Story Intelligence

- Story 4.2 establishes collection normalization in the users domain; binary models remain separate because their payload-safety requirements differ.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 4, Story 4.3]
- [Source: architecture spine — AD-1 through AD-5, AD-8, AD-10]
- [Source: PRD — FR-17, FR-20, FR-21, FR-22; binary limits open question]
- [Official REST v1 `getBinaryData`](https://documentation.infiniteblue.com/platform/getBinaryData.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Binary retrieval boundary, limit, malformed payload, and failure tests passed.
- Full suite and static quality gates passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added payload-safe immutable binary models and strict bounded Base64 decoding.
- Added validated `getBinaryData` retrieval through shared transport.

### File List

- bcic/endpoints/binary.py
- bcic/models/__init__.py
- bcic/models/binary.py
- tests/unit/test_endpoints.py
- tests/unit/test_endpoints_binary.py

### Change Log

- 2026-07-09: Implemented bounded binary retrieval; status set to review.
