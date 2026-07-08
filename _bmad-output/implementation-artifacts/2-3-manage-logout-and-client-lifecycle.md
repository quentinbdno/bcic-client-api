---
baseline_commit: f5d1d5b61997a09547ea18f43fabaa55a3858934
---

# Story 2.3: Manage Logout and Client Lifecycle

Status: review

## Story

As an SDK consumer,
I want explicit and safe session and HTTP resource cleanup,
so that long-running automation does not leak sessions or network resources.

## Acceptance Criteria

1. Logout calls REST v1 `logout` when authenticated and clears local state regardless of the handled outcome.
2. Logout without a session and repeated logout are safe and make no request.
3. `Client.close()` releases owned HTTP resources and is idempotent.
4. The context manager closes on exit without concealing an exception from the context body.

## Tasks / Subtasks

- [x] Implement idempotent auth logout and state clearing (AC: 1, 2)
- [x] Implement transport ownership-aware idempotent close (AC: 3)
- [x] Add client logout, close, and context-manager APIs (AC: 1-4)
- [x] Add lifecycle and exception-preservation tests (AC: 1-4)

## Dev Notes

- Official logout is GET `/rest/api/logout`, accepts `sessionId`, and returns a standard envelope.
- Injected `httpx.Client` is caller-owned and must not be closed; internally created clients are owned.
- After close, operations must fail with a typed SDK error rather than raw `httpx` behavior.
- Sources: [Architecture: AD-3, AD-8] [Epics: Story 2.3] [Official docs: logout]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Red: four lifecycle tests failed on absent logout, close, and context-manager APIs.
- Green/refactor: lifecycle tests and full 42-test suite pass; Ruff and strict mypy pass.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added idempotent logout, ownership-aware transport closure, and client context management.
- Verified 42 tests, Ruff, and strict mypy.

### File List

- bcic/auth.py
- bcic/client.py
- bcic/transport.py
- tests/unit/test_lifecycle.py
- _bmad-output/implementation-artifacts/2-3-manage-logout-and-client-lifecycle.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-07-08: Implemented safe logout and client lifecycle management.

## Status

review
