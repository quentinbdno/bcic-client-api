---
baseline_commit: f5d1d5b61997a09547ea18f43fabaa55a3858934
---

# Story 2.1: Build the REST v1 Transport and JSON Parser

Status: done

## Story

As an SDK endpoint developer,
I want a shared transport that executes REST v1 methods and normalizes JSON responses,
so that endpoint modules do not construct URLs or parse raw HTTP responses.

## Acceptance Criteria

1. GET and POST requests use `{base_url}/rest/api/{method_name}` and place parameters in query strings or JSON bodies respectively.
2. Successful JSON objects are normalized to typed JSON mappings; raw `httpx.Response` objects never cross the transport boundary.
3. Empty, malformed, non-object, or unsupported-format responses raise sanitized SDK API/validation exceptions.
4. Parsing remains behind an output-format-aware boundary so XML can be added without changing endpoint APIs.

## Tasks / Subtasks

- [x] Implement the JSON parser boundary (AC: 2, 3, 4)
  - [x] Add recursive JSON types and sanitized parse failures
- [x] Implement injectable REST v1 transport (AC: 1, 2)
  - [x] Support GET query parameters and POST JSON bodies
- [x] Add unit tests for URL construction, request placement, injection, and parse failures (AC: 1-4)

## Dev Notes

- Add `bcic/transport.py`; use injected `httpx.Client` or construct an owned client.
- `ResponseParser.parse(response, output_format)` owns decoding. JSON only for MVP; XML produces a typed error.
- Validate method names before URL construction to prevent arbitrary path execution.
- Preserve existing endpoint composition and configuration behavior.
- Sources: [Architecture: AD-2, AD-4, AD-8, AD-10] [Epics: Story 2.1] [Official REST v1 methods: `/rest/api/{method_name}`]

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Red: transport tests failed on the absent API error and transport module.
- Green/refactor: transport tests and full regression suite pass; Ruff and strict mypy pass.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added injectable REST v1 GET/POST transport, strict method-name validation, and sanitized JSON parsing.
- Verified 32 tests, Ruff, and strict mypy.

### File List

- bcic/exceptions.py
- bcic/transport.py
- tests/unit/test_transport.py
- _bmad-output/implementation-artifacts/2-1-build-the-rest-v1-transport-and-json-parser.md
- _bmad-output/implementation-artifacts/sprint-status.yaml

## Change Log

- 2026-07-08: Implemented REST v1 transport and JSON parser with unit coverage.

## Status

done
