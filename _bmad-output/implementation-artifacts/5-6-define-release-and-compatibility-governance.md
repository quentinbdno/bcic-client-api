# Story 5.6: Define Release and Compatibility Governance

Status: ready-for-dev

## Story

As an SDK maintainer,
I want documented versioning, release-note, and deprecation rules,
so that consumers can assess the compatibility risk of an upgrade.

## Acceptance Criteria

1. Governance defines the public API boundary, SemVer rules, and an explicit pre-1.0 policy where breaking changes are allowed only when documented with consumer impact and migration guidance.
2. Post-1.0 breaking changes to public endpoints, models, or exceptions require a major version; compatible additions/fixes map to minor/patch releases.
3. A changelog/release-note format records Added, Changed, Deprecated, Removed, Fixed, and Security entries plus migration guidance where applicable.
4. Post-1.0 public removals require a documented replacement and at least one minor release of `DeprecationWarning`; automated tests verify the standard warning category/message behavior without deprecating an arbitrary current API.

## Tasks / Subtasks

- [ ] Define versioning and public compatibility policy (AC: 1, 2)
  - [ ] Identify public imports/endpoints/models/exceptions versus explicitly internal modules and define pre/post-1.0 guarantees
  - [ ] Add a release decision table for major/minor/patch and pre-1.0 impact reporting
- [ ] Establish changelog and release process artifacts (AC: 1-3)
  - [ ] Add an Unreleased section/template and checklist for version, lock/build, quality gates, docs, migration notes, and tag
- [ ] Define and test deprecation mechanics (AC: 4)
  - [ ] Add a small internal warning helper only if it reduces inconsistency; use `DeprecationWarning`, replacement, removal target, and `stacklevel=2`
  - [ ] Test helper behavior on a private test callable; do not mark existing public methods deprecated without product direction
- [ ] Cross-check package metadata/docs and run all quality gates (AC: 1-4)

## Dev Notes

### Technical Requirements

- Create `docs/versioning.md`, `docs/releasing.md`, and root `CHANGELOG.md`.
- Follow Semantic Versioning 2.0.0 after 1.0. Before 1.0, document all public changes; breaking changes require prominent migration notes even if the numeric bump is minor.
- Define the public boundary concretely: `bcic.Client`, its endpoint properties/methods, documented public models, and SDK exception names. Leading-underscore symbols and transport/auth internals are not compatibility promises.
- Use standard-library `warnings.warn(..., DeprecationWarning, stacklevel=2)`. Do not use `FutureWarning` for developer-facing API deprecation.
- Package version remains `0.1.0` unless an actual release is being prepared; this story defines governance, not a release.

### Current State and Preservation

- `pyproject.toml` declares version `0.1.0`; no changelog/versioning/release docs exist.
- NFR-22/NFR-23 already establish the required pre-1.0, SemVer, and one-minor deprecation rules.
- Story 5.5 completes docstrings/examples; governance must treat those documented APIs as the compatibility surface.

### File Structure and Testing

- NEW: `CHANGELOG.md`, `docs/versioning.md`, `docs/releasing.md`.
- Optional NEW: `bcic/_deprecation.py` and focused unit test; keep helper private.
- UPDATE: docs index/API reference links only. No public API behavior change is required.

### Previous Story Intelligence

- Story 5.5 creates the inspectable documented public surface. Use it to enumerate compatibility promises and avoid accidentally including internals.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 5, Story 5.6]
- [Source: PRD — NFR-22, NFR-23; Versioning and Deprecation Policy]
- [Semantic Versioning 2.0.0](https://semver.org/)
- [Python `warnings` documentation](https://docs.python.org/3/library/warnings.html)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.

### File List

