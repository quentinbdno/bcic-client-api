---
baseline_commit: 425f2d91c8184000f9036ff76dc3ab21a6a91dbd
---

# Story 5.1: Establish Mockable Unit-Test Infrastructure

Status: review

## Story

As an SDK maintainer,
I want deterministic test infrastructure with injectable HTTP behavior,
so that SDK behavior can be verified without live BCIC credentials or tenants.

## Acceptance Criteria

1. Shared pytest fixtures construct configured clients with injectable `httpx.MockTransport`, capture ordered requests, and provide sanitized JSON success/error builders.
2. Tests can configure per-request or sequential responses and inspect method, URL, headers, query parameters, and bodies without exposing fixture credentials.
3. An autouse network guard causes accidental non-mocked HTTP attempts to fail clearly; the complete unit suite runs without environment credentials or a live tenant.
4. Existing tests are migrated to shared fixtures where this removes duplication without obscuring scenario-specific behavior, and all existing assertions remain effective.

## Tasks / Subtasks

- [x] Create typed reusable test builders and fixtures (AC: 1-3)
  - [x] Add request recorder, static/sequence handler, response builders, and configured-client fixture under `tests/unit/`
  - [x] Keep fixture secrets synthetic and never include production-looking tenant data
- [x] Add an explicit no-live-network guard (AC: 3)
  - [x] Permit only clients backed by `MockTransport`; fail accidental default `httpx` sends with an actionable message
  - [x] Ensure the guard does not patch pytest/httpx internals more broadly than necessary
- [x] Refactor representative existing tests and validate isolation (AC: 1-4)
  - [x] Reuse fixtures in auth, transport, lifecycle, methods, and endpoint tests where clearer
  - [x] Run the suite with BCIC environment variables removed and verify deterministic request order
- [x] Run pytest, Ruff format/check, and strict mypy (AC: 1-4)

## Dev Notes

### Technical Requirements

- Prefer `tests/unit/conftest.py` plus a focused helper module such as `tests/unit/fakes.py`; test-only helpers do not belong in `bcic/`.
- Reuse the production `Client(http_client=...)` seam and `httpx.MockTransport`; do not add `pytest-httpx`, `respx`, or another dependency.
- Use pytest `monkeypatch` for temporary environment/network guards; all mutations must be restored automatically.
- A sequence handler must fail on unexpected extra requests and include only sanitized method/path context.
- Preserve tests that intentionally instantiate `RestTransport` directly.

### Current State and Preservation

- Multiple tests define local handlers/client factories. Consolidate stable setup only; retain specialized retry/error handlers near their assertions.
- `Client` accepts an injected `httpx.Client`, and transport ownership deliberately avoids closing injected clients. Do not create a test-only public API.
- Pytest currently discovers only `tests/unit`; preserve that isolation.

### File Structure and Testing

- NEW: `tests/unit/conftest.py`, optionally `tests/unit/fakes.py`.
- UPDATE: existing unit tests only where fixture reuse improves clarity.
- No runtime files or dependencies should change unless a genuine missing injection seam is proven by a failing test.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 5, Story 5.1]
- [Source: architecture spine — AD-8]
- [Source: PRD — FR-23]
- [pytest fixtures](https://docs.pytest.org/en/stable/explanation/fixtures.html)
- [pytest monkeypatch guidance](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-07-09: Direct Poetry invocation unavailable; used the existing project
  virtual environment to execute equivalent gates.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added reusable typed request recording, response sequencing, JSON builders,
  configured client fixture, and a narrowly scoped no-live-network guard.
- Refactored representative authentication and transport tests onto shared fakes.
- Verified 157 tests pass with BCIC environment variables removed; Ruff and strict
  mypy pass.

### File List

- tests/unit/conftest.py
- tests/unit/fakes.py
- tests/unit/test_fakes.py
- tests/unit/test_auth.py
- tests/unit/test_transport.py

## Change Log

- 2026-07-09: Established deterministic offline unit-test infrastructure and
  migrated representative tests.
