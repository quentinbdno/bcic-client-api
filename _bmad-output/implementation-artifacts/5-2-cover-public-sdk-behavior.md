---
baseline_commit: 425f2d91c8184000f9036ff76dc3ab21a6a91dbd
---

# Story 5.2: Cover Public SDK Behavior

Status: done

## Story

As an SDK maintainer,
I want focused unit coverage for public behavior and critical internal boundaries,
so that regressions are detected before release.

## Acceptance Criteria

1. The unit suite covers configuration, authentication, lifecycle, transport/parsing, retries, exception mapping, pagination, models, records, users/permissions, binary operations, generic methods, and logging with representative success and failure paths.
2. Boundary tests assert documented SDK outcomes for malformed responses, exhausted retries, page limits/stalls, missing/denied resources, validation failures, and binary size/encoding violations.
3. Sensitive-value tests prove representative credentials, session IDs, tokens, raw bytes, and Base64 markers do not appear in logs, model reprs, or public exception text.
4. Every test remains offline, deterministic, behavior-focused, and passes without accepting raw dependency exceptions as public outcomes.

## Tasks / Subtasks

- [x] Build a requirement-to-test inventory before adding tests (AC: 1-4)
  - [x] Map FR-2 through FR-23 and every implemented public method/exception to existing test modules and identify actual gaps
  - [x] Do not duplicate coverage already supplied by focused Story 1-4 tests
- [x] Add missing public behavior and boundary tests (AC: 1-4)
  - [x] Cover cross-component flows through `Client` in addition to isolated model/transport units
  - [x] Add parameterized failure matrices while retaining readable scenario names
- [x] Add comprehensive leakage assertions (AC: 3)
  - [x] Centralize representative sensitive markers and check logs, errors, repr/str, and failed validation paths
- [x] Run all quality gates and document the resulting coverage matrix (AC: 1-4)
  - [x] Run pytest, Ruff format/check, and strict mypy

### Review Findings

- [x] [Review][Patch] Public model string representations still expose arbitrary dynamic sensitive values [bcic/models/common.py:29]

## Dev Notes

### Technical Requirements

- This story improves behavioral completeness, not line-count vanity. Do not add `pytest-cov` or a percentage threshold without an approved dependency decision.
- Use Story 5.1 fixtures and Story 4.5 logging/leakage helpers.
- Catch raw `httpx`, Pydantic, Base64, and parser exceptions at public boundaries; tests should explicitly fail if those types leak.
- Include tests for every public method's documented exceptions, but avoid asserting private implementation details unless the boundary itself is architectural.
- If Stories 3/4 are not implemented when this begins, HALT: the acceptance inventory cannot honestly cover absent public behavior.

### Current State and Preservation

- Existing Epic 1/2 tests cover 62 tests across package, configuration, auth, lifecycle, transport, retries/errors, models, endpoint composition, and generic methods.
- Stories 3/4 require their own focused tests; this story audits and fills gaps rather than replacing them.

### File Structure and Testing

- UPDATE/NEW under `tests/unit/`; use domain-specific files (`test_endpoints_records.py`, `test_endpoints_users.py`, `test_endpoints_binary.py`, `test_pagination.py`, `test_logging.py`).
- Optional NEW: `docs/testing.md` only if needed to preserve the coverage inventory for maintainers.
- Avoid test-only changes to public production signatures.

### Previous Story Intelligence

- Story 5.1 provides offline request builders and a no-network guard. All added HTTP tests must use them.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 5, Story 5.2]
- [Source: PRD — FR-22, FR-23; SM-1 through SM-3]
- [Source: architecture spine — AD-4, AD-5, AD-6, AD-8]
- [pytest fixture reference](https://docs.pytest.org/en/stable/reference/fixtures.html)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-07-09: Red-phase representation test exposed sensitive dynamic model
  fields; added sanitized SDK model representations.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Mapped FR-2 through FR-23 and the SDK exception surface to focused test
  modules in `docs/testing.md`.
- Added cross-component raw-exception, logging, and model-representation
  contracts with centralized sensitive markers.
- Verified 162 tests, Ruff format/check, and strict mypy pass.

### File List

- bcic/models/common.py
- docs/testing.md
- tests/unit/test_public_behavior_contract.py

## Change Log

- 2026-07-09: Completed the public-behavior coverage audit and closed the
  sensitive model representation gap.
