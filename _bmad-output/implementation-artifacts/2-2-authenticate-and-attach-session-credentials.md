---
baseline_commit: f5d1d5b61997a09547ea18f43fabaa55a3858934
---

# Story 2.2: Authenticate and Attach Session Credentials

Status: review

## Story

As an SDK consumer,
I want the client to authenticate and manage BCIC session credentials internally,
so that I can call endpoint methods without handling session identifiers myself.

## Acceptance Criteria

1. Explicit authentication calls REST v1 `login` and stores a valid returned `sessionId` only in private auth state.
2. The first authenticated request lazily authenticates and later requests reuse the session.
3. Auth state attaches `sessionId` centrally; endpoints never handle it.
4. Rejected credentials, login failures, and missing/invalid session results raise sanitized `AuthenticationError`.

## Tasks / Subtasks

- [x] Add encapsulated session authentication strategy (AC: 1, 3, 4)
  - [x] Send login credentials as headers and request JSON output
- [x] Integrate lazy authentication and credential attachment with transport (AC: 2, 3)
- [x] Expose explicit `Client.authenticate()` without exposing session state (AC: 1, 4)
- [x] Add unit tests for explicit/lazy auth, reuse, attachment, and sanitization (AC: 1-4)

## Dev Notes

- Add `bcic/auth.py`; private `_session_id` must not have a public accessor.
- Official REST v1 login supports GET/POST; use POST with `loginName` and `password` headers and `output=json`.
- Login itself must bypass lazy auth to avoid recursion.
- Attach session ID as a request header; documentation also permits URL parameters, but headers reduce leakage.
- Sources: [Architecture: AD-3, AD-4] [Epics: Story 2.2] [Official docs: login, Using REST to integrate with Platform]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Red: authentication tests failed because `bcic.auth` did not exist.
- Green/refactor: 6 auth tests and full 38-test suite pass; Ruff and strict mypy pass.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implemented explicit/lazy session authentication and centralized private session headers.
- Verified 38 tests, Ruff, and strict mypy.

### File List

- bcic/auth.py
- bcic/client.py
- bcic/endpoints/base.py
- bcic/exceptions.py
- bcic/transport.py
- tests/unit/test_auth.py
- _bmad-output/implementation-artifacts/2-2-authenticate-and-attach-session-credentials.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-07-08: Implemented REST v1 session authentication and attachment.

## Status

review
