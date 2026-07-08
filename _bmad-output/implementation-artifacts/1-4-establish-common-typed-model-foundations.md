---
baseline_commit: 735639e6fedc09bcbbf016cecf1cfc1898558cfa
---

# Story 1.4: Establish Common Typed Model Foundations

Status: review

## Story

As an SDK consumer,
I want common typed response, pagination, and dynamic-record models,
so that SDK results have a predictable shape while still supporting BCIC's variable record fields.

## Acceptance Criteria

1. Common response metadata and pagination data use reusable Pydantic 2 models with explicit mypy-compatible field types.
2. A dynamic record preserves object name, record identifier, and JSON-compatible variable field values without unrestricted `Any`.
3. Invalid public model input raises a typed, sanitized SDK `ValidationError`.

## Tasks / Subtasks

- [x] Establish the public model validation boundary (AC: 3)
  - [x] Add sanitized `ValidationError` to the SDK exception hierarchy.
  - [x] Add a strict immutable common model base that wraps Pydantic construction failures without embedding input.
- [x] Add reusable common and pagination models (AC: 1)
  - [x] Create typed `ResponseMetadata`, `PageMetadata`, and generic `Page[T]` models.
  - [x] Validate positive page/page-size values and non-negative totals.
- [x] Add the dynamic record foundation (AC: 2)
  - [x] Define recursive JSON-compatible value aliases without `Any`.
  - [x] Create `DynamicRecord` with non-empty object name, record identifier, and typed field mapping.
- [x] Export, test, and validate models (AC: 1–3)
  - [x] Export deliberate model names from `bcic.models`, without changing top-level `bcic.__all__`.
  - [x] Test valid serialization, generics, recursive dynamic values, invalid data, and sanitized errors.
  - [x] Run complete pytest, Ruff, mypy, and Poetry checks.

## Dev Notes

### Developer Context and Guardrails

- Use Pydantic 2 only. Models are immutable and reject unknown fields.
- `JSONValue` is the deliberate dynamic-data boundary: scalar JSON values plus recursive lists and string-keyed mappings. Do not use `Any`.
- Keep response metadata generic because the exact BCIC envelope is deferred to Story 2.1.
- Keep pagination traversal behavior out of models; `list_all()` belongs to Epic 3.
- SDK `ValidationError` must have a stable message based on model name only. Preserve the original Pydantic error through exception chaining for internal diagnosis.

### Architecture Compliance

- Follow AD-4, AD-5, and AD-6. Add `bcic/models/{__init__,common,records}.py`; extend `bcic/exceptions.py`; add `tests/unit/test_models.py`.
- Do not add endpoint methods, parsing, transport, authentication, or new dependencies.

### Previous Story Intelligence

- The package currently has immutable client configuration and four cached endpoint foundations.
- The test suite has 17 passing tests; top-level `bcic.__all__` remains exactly `["Client"]`.

### Latest Technical Information

- Pydantic 2 supports generic `BaseModel` subclasses directly and recursive typed models.
- `ConfigDict(frozen=True, extra="forbid")` supplies the shared immutable/strict-extra policy.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 1, Story 1.4]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-bcic-client-api-2026-07-08/ARCHITECTURE-SPINE.md` — AD-4, AD-5, AD-6]
- [Source: `_bmad-output/planning-artifacts/prds/prd-bcic-client-api-2026-07-08/prd.md` — FR-20, FR-21, NFR-5, NFR-7]
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- RED: model tests failed during collection because `bcic.models` did not exist.

### Implementation Plan

- Create the sanitized common model base, then layer reusable metadata,
  pagination, and recursive dynamic-record contracts on it.
- Validate direct construction and serialization before the full regression run.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added strict immutable response metadata, pagination metadata, generic page,
  and recursive JSON-compatible dynamic record models.
- Added sanitized SDK model validation failures without unrestricted `Any`;
  all 22 tests and Poetry/Ruff/mypy checks pass.

### File List

- `bcic/exceptions.py`
- `bcic/models/__init__.py`
- `bcic/models/common.py`
- `bcic/models/records.py`
- `tests/unit/test_models.py`
- `_bmad-output/implementation-artifacts/1-4-establish-common-typed-model-foundations.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-07-08: Added common typed response, pagination, and dynamic-record model
  foundations with sanitized validation failures.
