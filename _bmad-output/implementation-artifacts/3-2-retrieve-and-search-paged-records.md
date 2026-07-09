# Story 3.2: Retrieve and Search Paged Records

Status: ready-for-dev

## Story

As an SDK consumer,
I want to retrieve or search a page of records using typed options,
so that I can process bounded record sets without constructing URLs or query strings.

## Acceptance Criteria

1. The records endpoint exposes typed page retrieval using REST v1 `getPage`, with validated view ID, zero-based start row, positive page size, and typed optional filters/field selection.
2. A successful response is normalized into shared `Page[DynamicRecord]`; page metadata is independent of the REST method name and uses deterministic values when BCIC omits totals.
3. Search/select behavior, if exposed by this story, uses a typed criteria object that constructs the documented query internally; callers are not required to pass a raw SQL/query string through the high-level endpoint.
4. Invalid bounds/criteria and malformed or partially valid pages raise a sanitized SDK exception before any partial page is returned.

## Tasks / Subtasks

- [ ] Define immutable typed page options and response normalization (AC: 1-4)
  - [ ] Model `view_id`, `start_row`, `page_size`, `composite`, optional object/field names, and optional equality filter
  - [ ] Normalize the full record collection atomically and derive page number/completion metadata without fabricating unavailable totals
- [ ] Implement one-page record retrieval through `getPage` (AC: 1, 2, 4)
  - [ ] Map options to `viewId`, `startRow`, `rowsPerPage`, `composite`, `objNames`, `fieldList`, `filterName`, `filterValue`, `onlyViewFields`, and `output`
  - [ ] Keep method constants and response-shape handling centralized
- [ ] Add a safe typed search/select surface only if its result can satisfy `Page[DynamicRecord]` (AC: 3, 4)
  - [ ] Do not expose raw SQL as a high-level convenience; `client.methods` remains the explicit lower-level escape hatch
  - [ ] Account for official `search` returning IDs and `selectQuery` returning 2D rows, not record objects
- [ ] Add tests and run all quality gates (AC: 1-4)
  - [ ] Cover first/later/short/empty pages, filters, invalid options, malformed item/page data, and no partial return
  - [ ] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Create `bcic/pagination.py` for paging options/state and extend `bcic/endpoints/records.py` plus record models.
- `PageMetadata` currently requires exact `total_items` and `total_pages`. Official `getPage` does not document totals. Adjust the shared model deliberately (for example optional totals plus `start_row`, returned count, and `has_more`) rather than inserting false totals.
- Official `getPage` is GET and is view-based: it requires `viewId`, not object name. Preserve that contract in naming and types.
- A full page (`len(items) == page_size`) does not prove another page exists; it is a conservative continuation signal for Story 3.3 unless a response supplies authoritative metadata.
- `search` accepts a query and optional `objName` but returns IDs; `selectQuery` accepts `startRow`, `maxRows`, and SQL and returns a 2D array. Do not claim these are record pages without a documented hydration strategy.

### Architecture Compliance

- AD-5: page items are typed `DynamicRecord`; validate all items before constructing a page.
- AD-6: options and page state belong in `pagination.py`, not endpoint-specific traversal code.
- AD-2/AD-3/AD-4: endpoints do not build HTTP or attach sessions; public failures remain SDK exceptions.

### Current State and Preservation

- Story 3.1 is the expected prerequisite for single-record normalization; reuse it for each `getPage` item.
- Existing `Page`/`PageMetadata` are strict frozen Pydantic models. Preserve their generic public contract while correcting metadata semantics.
- `RestTransport` parser currently accepts only top-level mappings, while official `getPage`, `search`, and `selectQuery` JSON examples may be top-level arrays. This story must extend normalization at the parser boundary without weakening malformed-response checks or breaking existing mapping consumers.

### File Structure and Testing

- NEW: `bcic/pagination.py`, `tests/unit/test_pagination.py`.
- UPDATE: `bcic/endpoints/records.py`, `bcic/models/common.py`, `bcic/models/records.py`, exports, and `bcic/transport.py` only as required for documented array responses.
- Mock all HTTP; assert exact parameter names and atomic failure when any item is invalid.

### Previous Story Intelligence

- Story 3.1 defines the canonical mapping-to-`DynamicRecord` normalization. Do not create a second record parser.
- No implementation learnings are available yet because 3.1 is currently contexted, not implemented.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 3, Story 3.2]
- [Source: architecture spine — AD-2, AD-5, AD-6, AD-8, AD-10]
- [Official REST v1 `getPage`](https://documentation.infiniteblue.com/platform/getPage.htm)
- [Official REST v1 `search`](https://documentation.infiniteblue.com/platform/search.htm)
- [Official REST v1 `selectQuery`](https://documentation.infiniteblue.com/platform/selectQuery.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

