---
baseline_commit: f5d1d5b61997a09547ea18f43fabaa55a3858934
---

# Story 2.5: Execute Controlled Generic REST v1 Methods

Status: review

## Story

As an SDK consumer,
I want controlled access to documented REST v1 methods not yet promoted to domain endpoints,
so that I can use broader BCIC capabilities without bypassing SDK safeguards.

## Acceptance Criteria

1. `client.methods.execute()` accepts a validated method name, JSON-compatible typed parameters, GET/POST, and optional output format without accepting raw URLs or requests.
2. Calls use shared authentication, transport, retry, parser, and exception behavior and return a typed JSON mapping.
3. Invalid names, methods, parameter shapes, and output options fail with SDK `ValidationError` before network execution.
4. Docstrings identify domain endpoints as preferred and `client.methods` as the lower-level escape hatch.

## Tasks / Subtasks

- [x] Define validated generic method request types (AC: 1, 3)
- [x] Implement `MethodsEndpoint.execute()` through shared transport (AC: 1, 2, 4)
- [x] Add unit tests for valid GET/POST calls and preflight rejection (AC: 1-4)

## Dev Notes

- Permit method identifiers matching `^[A-Za-z][A-Za-z0-9_]*$`; prohibit slashes, schemes, query fragments, and path traversal.
- Restrict HTTP methods to GET and POST for this story.
- Parameters must recursively contain JSON-compatible values with string keys.
- Output defaults to client configuration and remains parser-controlled.
- Sources: [Architecture: AD-1, AD-2, AD-4, AD-10] [Epics: Story 2.5]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Red: six endpoint tests failed because `MethodsEndpoint.execute()` was absent.
- Green/refactor: focused tests and full 62-test suite pass; Ruff and strict mypy pass.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added a controlled lower-level GET/POST method wrapper with recursive JSON validation and shared SDK safeguards.
- Verified 62 tests, Ruff, and strict mypy.

### File List

- bcic/endpoints/methods.py
- bcic/transport.py
- tests/unit/test_methods_endpoint.py
- _bmad-output/implementation-artifacts/2-5-execute-controlled-generic-rest-v1-methods.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-07-08: Implemented controlled generic REST v1 method execution.

## Status

review
