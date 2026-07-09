# Story 5.5: Provide Examples and Public API Docstrings

Status: ready-for-dev

## Story

As an SDK consumer,
I want runnable examples and complete public method docstrings,
so that I can understand supported operations directly from code and project resources.

## Acceptance Criteria

1. `examples/` contains focused scripts for authentication/lifecycle, records, pagination, roles/permissions, binary handling, and error handling using environment configuration or obvious placeholders.
2. Every public class, method, model, and exception has a docstring describing purpose; callable docstrings document parameters, return values, and relevant SDK exceptions accurately.
3. Examples import only supported public APIs, never execute on import, contain no secrets, and remain outside runtime package code.
4. Automated validation detects syntax errors, stale imports/signatures, import-time network calls, embedded secret markers, and materially missing public docstrings.

## Tasks / Subtasks

- [ ] Add safe focused examples (AC: 1, 3)
  - [ ] Use `main()` plus `if __name__ == "__main__"` guards and `Client.from_env()`/context management
  - [ ] Keep mutating/binary examples explicit and non-executing by default where accidental operations would be unsafe
- [ ] Audit and complete public API docstrings (AC: 2)
  - [ ] Cover top-level exports, `Client`, endpoint methods, public models, and exception classes
  - [ ] Keep internal/private symbols concise and do not promote them to public API
- [ ] Add automated example/docstring contract tests (AC: 3, 4)
  - [ ] Compile/import examples without running `main`; inspect supported public symbols/signatures; scan for sensitive literals
- [ ] Run pytest, Ruff format/check, and strict mypy (AC: 1-4)

## Dev Notes

### Technical Requirements

- Required examples: `examples/authentication.py`, `records.py`, `pagination.py`, `permissions.py`, `binary.py`, `error_handling.py`.
- Do not use real tenant names, record IDs, filenames, credentials, or tokens. Use environment inputs and clearly fake values.
- Upload/delete examples must require explicit user edits/confirmation in `main()` and must not run during validation.
- Public docstrings should use one consistent readable style; no documentation generator dependency is required.
- Tests can use `ast`, `compile`, `importlib`, and `inspect` from the standard library.

### Current State and Preservation

- Existing public methods have short purpose docstrings but generally omit detailed parameters/returns/raises.
- No examples directory exists.
- Top-level `bcic` intentionally exports only `Client`; models/exceptions remain public through their modules unless intentionally re-exported.

### File Structure and Testing

- NEW: example files and `tests/unit/test_examples_docs.py`.
- UPDATE: public modules throughout `bcic/` for docstrings only; behavior changes are out of scope.
- Do not weaken strict mypy to accommodate examples; either type-check examples explicitly or validate syntax/import contracts separately.

### Previous Story Intelligence

- Story 5.4 establishes canonical wording and signatures. Examples/docstrings must align with it, not create a competing contract.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 5, Story 5.5]
- [Source: PRD — FR-21, FR-24; NFR-13 through NFR-15]
- [Source: architecture spine — public API and structural seed]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

