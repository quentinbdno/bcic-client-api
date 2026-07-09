---
baseline_commit: 34f7e1fe4e572f92b219073dd796bb200da563d1
---

# Story 3.3: Traverse All Record Pages Safely

Status: review

## Story

As an SDK consumer,
I want a bounded helper that retrieves every matching record page,
so that I can automate complete retrieval without writing pagination loops.

## Acceptance Criteria

1. `client.records.list_all(...)` delegates every page request to the Story 3.2 one-page operation and returns typed `DynamicRecord` values in stable page order.
2. Positive `page_size`, `max_pages`, and `max_items` safeguards are validated before network execution; reaching a safeguard before natural completion raises a documented typed limit exception and never silently truncates.
3. Traversal stops naturally on authoritative completion metadata, an empty page, or a short page; it detects non-advancing pagination and raises rather than looping.
4. A failed page uses normal transport retry/exception behavior, is not skipped, and does not cause the helper itself to replay earlier successful pages.

## Tasks / Subtasks

- [x] Implement a reusable bounded pagination traversal helper (AC: 1-4)
  - [x] Put traversal state and limits in `bcic/pagination.py`; accept a typed page-fetch callback
  - [x] Track requested offsets, yielded item count, completion, and non-advancing states deterministically
- [x] Expose `RecordsEndpoint.list_all()` by composing the one-page method (AC: 1-4)
  - [x] Pass the same typed selection/filter options on every page and advance only the paging cursor
  - [x] Choose and document eager `list[DynamicRecord]` semantics; do not return partial data on limit/failure
- [x] Add traversal tests and run all quality gates (AC: 1-4)
  - [x] Cover empty, single short, exact-full then empty, multi-page, page/item limit, invalid limit, non-advancing page, and middle-page failure
  - [x] Assert request sequence has no skipped or duplicate offsets; run pytest, Ruff, and mypy

## Dev Notes

### Technical Requirements

- Reuse Story 3.2 page options, `Page`, and page-fetch implementation. Endpoint code should only adapt record options into the shared pagination helper.
- Define a dedicated SDK exception such as `PaginationLimitError(ValidationError)` if limits are exceptional; make the public contract explicit and export it consistently.
- Validate safeguards before fetching. If adding the next page would exceed `max_items`, raise without returning a truncated list.
- Do not implement independent retries. `RestTransport.execute()` owns retries per page; traversal calls each logical page once.
- Avoid offset arithmetic based solely on returned count when the backend contract expects fixed `rowsPerPage`; advance by the documented page cursor/size and verify progress.

### Architecture Compliance

- AD-6 is mandatory: generic traversal belongs in `bcic/pagination.py`.
- AD-4: limit and stalled-pagination failures are typed SDK exceptions.
- AD-8: unit tests use deterministic page callbacks and mocked HTTP, never a live tenant.

### Current State and Preservation

- Story 3.2 creates pagination primitives and one-page retrieval. Preserve its validation and request mapping; do not bypass it.
- Existing transport retries `NetworkError`, `RateLimitError`, and `ServerError`. Pagination must neither wrap nor retry those independently.

### File Structure and Testing

- UPDATE: `bcic/pagination.py`, `bcic/endpoints/records.py`, `bcic/exceptions.py` and exports if a new public exception is introduced.
- UPDATE/NEW tests: `tests/unit/test_pagination.py`, `tests/unit/test_endpoints_records.py`.
- Prefer pure unit tests for the generic traversal state machine plus endpoint integration tests for request offsets.

### Previous Story Intelligence

- Story 3.2 establishes optional/authoritative page metadata semantics. Natural completion must use those semantics, not invented totals.
- No runtime implementation notes are available while 3.2 remains ready-for-dev.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.3]
- [Source: architecture spine — AD-4, AD-6, AD-8]
- [Source: PRD — FR-19]
- [Official REST v1 `getPage`](https://documentation.infiniteblue.com/platform/getPage.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-07-09: Implemented and exercised the bounded traversal state machine.

### Implementation Plan

- Keep traversal generic and eager, validate limits before I/O, and delegate every logical page fetch exactly once.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added bounded page and item safeguards, deterministic offsets, completion detection, and `PaginationLimitError`.
- Validated no replay or partial return behavior with pure and endpoint-level tests.
- Validated with 98 passing tests, Ruff format/check, and strict mypy.

### File List

- bcic/endpoints/records.py
- bcic/exceptions.py
- bcic/pagination.py
- tests/unit/test_endpoints_records.py
- tests/unit/test_pagination.py

## Change Log

- 2026-07-09: Added safe bounded traversal and record `list_all`.
