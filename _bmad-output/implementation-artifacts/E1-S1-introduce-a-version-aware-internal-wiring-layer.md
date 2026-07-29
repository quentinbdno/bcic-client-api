---
baseline_commit: 7473cec79fcf37a8f0d3c8e00d3176c23176cdbb
---

# Story E1-S1: Introduce a Version-Aware Internal Wiring Layer

Status: review

## Story

As an SDK maintainer,
I want a version-aware internal wiring layer,
so that the client can resolve v1 or v2 adapters from `api_version` without mixing adapter logic.

## Acceptance Criteria

1. **Given** a `Client` initialized with `api_version=v1`  
   **When** the client resolves its internal adapters  
   **Then** it uses the existing v1 adapter set and preserves current behavior.

2. **Given** a `Client` initialized with `api_version=v2`  
   **When** the client resolves its internal adapters  
   **Then** it uses a distinct v2 adapter set.

3. **Given** endpoint modules for either version  
   **When** their request logic is inspected  
   **Then** no endpoint module contains mixed v1/v2 branching logic.

## Tasks / Subtasks

- [x] Add a version-aware composition/factory layer for adapter resolution (AC: 1, 2)
  - [x] Define the internal selection boundary for `api_version`.
  - [x] Keep version resolution isolated from endpoint request code.
- [x] Wire `Client` to the version-aware layer without changing the public contract (AC: 1, 2)
  - [x] Preserve v1 as the default path.
  - [x] Ensure the existing public client surface remains stable.
- [x] Add tests proving version resolution and adapter isolation (AC: 1, 2, 3)
  - [x] Verify v1 resolves to the current adapter path.
  - [x] Verify v2 resolves to a distinct adapter path.
  - [x] Verify endpoint modules do not branch on version internally.

## Dev Notes

- Keep this story inside the internal wiring boundary; do not add new endpoint behavior yet.
- The goal is selection and composition only. Request routing, auth semantics, and endpoint payload handling belong to downstream stories.
- Preserve the current public `Client` contract while adding version selection behind the scenes.

## References

- [Source: `_bmad-output/planning-artifacts/epics-bcic-client-api-rest-v2-readiness-2026-07-29.md` — E1-S1]
- [Source: `_bmad-output/planning-artifacts/epics-bcic-client-api-rest-v2-2026-07-28.md` — Epic 1]

## Dev Agent Record

### Debug Log

- 2026-07-29: Red phase confirmed with `.venv/bin/python -m pytest tests/unit/test_internal_wiring.py`; collection failed because `bcic._wiring` did not exist.
- 2026-07-29: Focused story tests passed after implementation with `.venv/bin/python -m pytest tests/unit/test_internal_wiring.py`.
- 2026-07-29: Full regression passed with `.venv/bin/python -m pytest`.
- 2026-07-29: Quality gates passed with `.venv/bin/python -m ruff check .` and `.venv/bin/python -m mypy`.

### Completion Notes

- Added private version-aware adapter resolution in `bcic._wiring`, with distinct v1 and v2 REST adapters and an adapter-set factory.
- Wired `Client` through the private adapter-set boundary while preserving constructor behavior and default v1 resolution.
- Refactored `RestTransport` to delegate version-specific URL/header construction to the resolved adapter instead of branching internally on `api_version`.
- Added tests covering v1 default resolution, distinct v2 resolution, current v1/v2 request paths, and endpoint-module isolation from version branching.

## File List

- `_bmad-output/implementation-artifacts/E1-S1-introduce-a-version-aware-internal-wiring-layer.md`
- `bcic/_wiring.py`
- `bcic/client.py`
- `bcic/transport.py`
- `tests/unit/test_internal_wiring.py`

## Change Log

- 2026-07-29: Implemented E1-S1 version-aware internal wiring layer and moved story to review.
