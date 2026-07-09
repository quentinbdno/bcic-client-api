---
baseline_commit: b1f383f1fc11ad0e3d50214a46df2b647f37a06d
---

# Story 4.5: Enforce Safe Operational Logging

Status: review

## Story

As an SDK consumer,
I want useful but sanitized SDK logging,
so that I can diagnose operations without exposing credentials, sessions, or binary content.

## Acceptance Criteria

1. Every SDK module that emits events uses `logging.getLogger(__name__)`; library code never calls `print()`, configures handlers/root logging, or changes the consuming application's log level.
2. Authentication, request lifecycle, retry, endpoint, and failure events provide useful method/status/attempt context at conventional levels without logging request/response bodies.
3. A centralized sanitizer/redaction helper removes credentials, session IDs, tokens, authorization values, binary bytes, and Base64 payloads from structured context and exception-safe messages.
4. Automated tests inject representative secrets and binary markers and prove they are absent from captured logs and public exception text while non-sensitive operation context remains available.

## Tasks / Subtasks

- [x] Define centralized safe logging utilities and policy (AC: 1-4)
  - [x] Create module logger/redaction helpers with an explicit sensitive-key policy and recursive mapping/sequence handling
  - [x] Return redacted copies; never mutate caller data, inspect arbitrary object internals, or rely on regex-only secret discovery
- [x] Add operational logging at shared boundaries (AC: 1-3)
  - [x] Log method lifecycle and terminal failures in transport without URLs/query/body/header values
  - [x] Log authentication/session lifecycle without usernames/passwords/session IDs and endpoint operation names without payloads
  - [x] Avoid duplicate log records for the same event across endpoint and transport layers
- [x] Audit the package and harden exception diagnostics (AC: 1-4)
  - [x] Confirm no `print()`, handler configuration, raw payload/header logging, or secret-bearing exception interpolation exists
  - [x] Preserve exception types/causes while keeping public messages sanitized
- [x] Add capture tests and run all quality gates (AC: 1-4)
  - [x] Cover credentials, session/token/header values, nested mappings, binary bytes/Base64 markers, auth success/failure, retries, endpoint operations, and consumer-selected log levels
  - [x] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Create `bcic/utils/__init__.py` and `bcic/utils/logging.py`; use only standard-library `logging`.
- Prefer logging fixed message templates plus allowlisted scalar context (`method_name`, HTTP method, status code/class, retry attempt, endpoint operation). Never pass parameter mappings, headers, URLs with queries, response payloads, credentials, sessions, or binary content.
- Sensitive keys include case-insensitive variants of password, credential, authorization, session/sessionId, token, secret, cookie, `value` for binary calls, `fileData`, and binary/content/body/payload fields.
- Redaction is defense in depth, not permission to log arbitrary payloads. Sanitizer output should replace sensitive values with a fixed marker and handle recursion limits/cycles safely.
- Tenacity retry logging may use a safe callback or transport-owned attempt logging; preserve current retry count/wait semantics.
- Public exceptions currently use fixed sanitized messages. Audit and retain exception chaining for debugging without formatting raw causes into messages.

### Architecture Compliance

- AD-3/AD-4: authentication state stays private and failures remain sanitized.
- Architecture logging convention: module-level `logging.getLogger(__name__)`, no global configuration.
- NFR-10/FR-22: credentials, sessions, tokens, and binary payloads never appear.
- AD-8: deterministic `caplog` tests use mocked HTTP only.

### Current State and Preservation

- Current library contains no operational logging and no `print()` calls. Add logging primarily in `auth.py` and `transport.py`, then only endpoint-level events that add distinct domain context.
- `ClientConfig.password` is a Pydantic `SecretStr`; never call `get_secret_value()` for logging.
- `SessionAuth` owns private session state; log state transitions only, not identifiers.
- Binary Stories 4.3-4.4 establish content-free model repr and errors. Logging must preserve those guarantees.

### File Structure and Testing

- NEW: `bcic/utils/__init__.py`, `bcic/utils/logging.py`, `tests/unit/test_logging.py`.
- UPDATE: `bcic/auth.py`, `bcic/transport.py`, and endpoint modules only where distinct operation logs are justified.
- Run `rg -n 'print\\(|basicConfig|addHandler|setLevel' bcic tests` as an audit alongside pytest/Ruff/mypy.

### Previous Story Intelligence

- Story 4.4 treats both raw bytes and Base64 as sensitive and ensures typed upload results retain neither. Apply the same rule across logging.
- Stories 4.1-4.4 use shared transport execution, making transport the primary lifecycle logging boundary.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 4, Story 4.5]
- [Source: architecture spine — AD-3, AD-4, logging consistency convention]
- [Source: PRD — FR-22; NFR-5, NFR-10, NFR-12]
- [Python logging library guidance](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Sanitizer, capture, context preservation, and consumer log-level tests passed.
- Full suite, static gates, and forbidden logging configuration audit passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added recursive non-mutating redaction utilities with cycle/depth protection.
- Added fixed-template, payload-free authentication and transport lifecycle logging.
- Audited public exception messages and package logging configuration.

### File List

- bcic/auth.py
- bcic/transport.py
- bcic/utils/__init__.py
- bcic/utils/logging.py
- tests/unit/test_logging.py

### Change Log

- 2026-07-09: Implemented safe operational logging and redaction; status set to review.
