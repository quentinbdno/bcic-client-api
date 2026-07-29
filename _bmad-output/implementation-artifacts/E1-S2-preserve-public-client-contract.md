---
baseline_commit: 7473cec79fcf37a8f0d3c8e00d3176c23176cdbb
---

# Story E1-S2: Preserve Public Client Contract

Status: ready-for-dev

## Story

As an SDK consumer,
I want the existing client contract to remain stable,
so that current v1 usage continues to work and `api_version` defaults safely to v1.

## Acceptance Criteria

1. **Given** existing v1 usage patterns  
   **When** the SDK is upgraded  
   **Then** those usage patterns continue to work unchanged.

2. **Given** a `Client` constructed without an explicit `api_version`  
   **When** the client is initialized  
   **Then** it defaults to v1.

3. **Given** the current public endpoint property names  
   **When** the SDK is updated for versioned support  
   **Then** those names remain unchanged.

## Tasks / Subtasks

- [ ] Preserve constructor defaults and current v1 behavior (AC: 1, 2)
  - [ ] Keep v1 as the default runtime behavior.
  - [ ] Avoid introducing breaking constructor changes.
- [ ] Keep the public client surface stable (AC: 1, 3)
  - [ ] Retain current endpoint property names.
  - [ ] Prevent versioning changes from leaking into the public API shape.
- [ ] Add regression coverage for defaulting and backward compatibility (AC: 1, 2, 3)
  - [ ] Verify default construction still selects v1.
  - [ ] Verify the documented public endpoint names are unchanged.

## Dev Notes

- This story is about preserving consumer behavior, not adding new endpoint functionality.
- Version selection should remain an internal concern when possible; public API changes must be avoided unless explicitly required.
- Keep any compatibility checks focused on the stable v1 surface.

## References

- [Source: `_bmad-output/planning-artifacts/epics-bcic-client-api-rest-v2-readiness-2026-07-29.md` — E1-S2]
- [Source: `_bmad-output/planning-artifacts/epics-bcic-client-api-rest-v2-2026-07-28.md` — Epic 1]
