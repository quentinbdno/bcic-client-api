---
baseline_commit: f5d1d5b61997a09547ea18f43fabaa55a3858934
---

# Story 2.4: Map Failures and Apply Retry Policy

Status: review

## Story

As an SDK consumer,
I want predictable typed failures and conservative retries,
so that my application can respond correctly without interpreting HTTP or BCIC internals.

## Acceptance Criteria

1. Authentication, authorization, validation, rate-limit, not-found, server, and generic API errors are distinct `BCICError` subclasses.
2. HTTP errors, BCIC error envelopes, network failures, timeouts, session failures, permission failures, and unknown failures map to sanitized SDK errors.
3. Transient failures retry deterministically using configured limits/delay and exhausted failures retain the appropriate SDK type.
4. Authentication, authorization, validation, and other non-transient failures are not retried.

## Tasks / Subtasks

- [x] Complete the public exception hierarchy with sanitized context (AC: 1)
- [x] Map HTTP, network, timeout, and BCIC envelope failures (AC: 2)
- [x] Add configured tenacity retry policy for transient failures only (AC: 3, 4)
- [x] Add mapping, retry-count, exhaustion, and non-retry tests (AC: 1-4)

## Dev Notes

- Retry count means additional attempts after the initial request (`max_retries + 1` total attempts).
- Retry network/timeout, HTTP 429, and HTTP 5xx. Do not retry 4xx auth/permission/validation/not-found.
- Never include request headers, credentials, session IDs, raw bodies, or binary data in public error messages.
- Sources: [Architecture: AD-4, AD-8] [Epics: Story 2.4]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Red: error/retry tests failed on the incomplete exception hierarchy.
- Green/refactor: 14 focused tests and full 56-test suite pass; Ruff and strict mypy pass.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added sanitized typed failure mapping and deterministic transient-only retries.
- Verified 56 tests, Ruff, and strict mypy.

### File List

- bcic/client.py
- bcic/exceptions.py
- bcic/transport.py
- tests/unit/test_errors_retry.py
- _bmad-output/implementation-artifacts/2-4-map-failures-and-apply-retry-policy.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-07-08: Implemented failure mapping and configurable retry policy.

## Status

review
