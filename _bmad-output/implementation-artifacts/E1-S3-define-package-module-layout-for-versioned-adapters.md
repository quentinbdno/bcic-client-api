---
baseline_commit: 7473cec79fcf37a8f0d3c8e00d3176c23176cdbb
---

# Story E1-S3: Define Package/Module Layout for Versioned Adapters

Status: ready-for-dev

## Story

As a maintainer,
I want a physically separated package and module layout for versioned adapters,
so that v1 and v2 internals are easy to understand and shared primitives stay centralized.

## Acceptance Criteria

1. **Given** the repository layout for SDK internals  
   **When** versioned adapters are introduced  
   **Then** v1 and v2 internals are physically separated.

2. **Given** shared functionality needed by both versions  
   **When** the module structure is organized  
   **Then** shared primitives remain in common modules.

3. **Given** a maintainer unfamiliar with the codebase  
   **When** they inspect the structure  
   **Then** they can identify the version boundary within five minutes.

## Tasks / Subtasks

- [ ] Define the versioned adapter module layout (AC: 1, 2, 3)
  - [ ] Separate v1 and v2 internals into distinct module areas.
  - [ ] Keep shared primitives in common modules.
- [ ] Ensure the layout is discoverable for maintainers (AC: 3)
  - [ ] Choose module names and placement that make the version boundary obvious.
  - [ ] Avoid ambiguous mixed-version locations.
- [ ] Add tests or checks that enforce the intended separation (AC: 1, 2, 3)
  - [ ] Verify shared modules are reused instead of duplicated where appropriate.
  - [ ] Verify the versioned layout remains clearly separated.

## Dev Notes

- This story is structural only. It should not introduce v2 transport behavior or endpoint logic yet.
- Keep shared primitives centralized so later v2 stories can reuse them cleanly.
- Favor explicit, maintainable naming over clever abstractions.

## References

- [Source: `_bmad-output/planning-artifacts/epics-bcic-client-api-rest-v2-readiness-2026-07-29.md` — E1-S3]
- [Source: `_bmad-output/planning-artifacts/epics-bcic-client-api-rest-v2-2026-07-28.md` — Epic 1]
