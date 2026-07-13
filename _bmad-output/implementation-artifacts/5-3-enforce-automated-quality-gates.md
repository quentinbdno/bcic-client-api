---
baseline_commit: 425f2d91c8184000f9036ff76dc3ab21a6a91dbd
---

# Story 5.3: Enforce Automated Quality Gates

Status: done

## Story

As an SDK maintainer,
I want reproducible automated checks for tests, style, and typing,
so that every releasable change meets the same baseline quality standard.

## Acceptance Criteria

1. `pyproject.toml` and committed `poetry.lock` reproducibly define runtime/development dependencies and centralized pytest, Ruff, and strict mypy settings.
2. One documented local command sequence and a GitHub Actions workflow run `pytest`, `ruff check`, `ruff format --check`, and `mypy`; any failure fails the job.
3. CI runs on the minimum supported Python 3.12 and a current Python 3.x version, uses Poetry dependency installation, and requires no BCIC credentials or network access during tests.
4. Dependency additions remain separated by runtime/development purpose and require an SDK-level rationale; convenience-only packages are not introduced.

## Tasks / Subtasks

- [x] Audit and tighten centralized tool/dependency configuration (AC: 1, 4)
  - [x] Confirm lockfile matches `pyproject.toml`, strict mypy scopes library code, and Ruff/pytest discovery is intentional
  - [x] Add package typing marker/config only if required by the public typing contract
- [x] Add reproducible GitHub Actions quality workflow (AC: 2, 3)
  - [x] Use a Python matrix for 3.12 and one current supported version; install Poetry, then `poetry install`
  - [x] Run all four gates with no secrets and least-required workflow permissions
- [x] Document local quality commands and dependency policy (AC: 2, 4)
  - [x] Keep commands identical in meaning to CI and explain runtime versus dev placement
- [x] Execute the full workflow locally where available (AC: 1-4)
  - [x] Run lock consistency/install validation, pytest, Ruff lint/format checks, and strict mypy

## Dev Notes

### Technical Requirements

- Create `.github/workflows/quality.yml`; pin third-party actions to stable major versions already recommended by official GitHub docs and grant `contents: read`.
- Use `poetry run pytest`, `poetry run ruff check .`, `poetry run ruff format --check .`, and `poetry run mypy`.
- Do not use auto-fix commands in CI.
- Do not add a coverage service, pre-commit framework, task runner, or cache action unless independently justified.
- Python 3.12 syntax is used by the package. A newer matrix entry verifies forward compatibility but does not change `requires-python`.

### Current State and Preservation

- `pyproject.toml` already declares Python `>=3.12,<4.0`, runtime dependencies, dev dependencies, and baseline tool configuration; `poetry.lock` is committed.
- No `.github/` workflow or local quality documentation exists.
- Preserve Poetry as the sole dependency source of truth.

### File Structure and Testing

- NEW: `.github/workflows/quality.yml`, `docs/contributing.md` (or a concise root contributing file).
- UPDATE: `pyproject.toml`/`poetry.lock` only for proven configuration or lock consistency needs.

### Previous Story Intelligence

- Story 5.2 must leave every gate green. CI should invoke those existing gates rather than invent another test path.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 5, Story 5.3]
- [Source: architecture spine — AD-7, AD-8]
- [Source: PRD — NFR-7, NFR-8, NFR-17 through NFR-21]
- [Ruff formatter check](https://docs.astral.sh/ruff/formatter/)
- [mypy command/config behavior](https://mypy.readthedocs.io/en/stable/command_line.html)
- [GitHub Python workflow guidance](https://docs.github.com/en/actions/tutorials/build-and-test-code/python)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- 2026-07-09: Poetry was unavailable locally; lock metadata/content hash was
  audited and equivalent gates ran from the existing locked environment.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added a least-privilege GitHub Actions matrix for Python 3.12 and 3.14 using
  Poetry and the four required quality commands.
- Documented contributor setup, identical local gates, and runtime/dev
  dependency placement policy.
- Verified 164 tests, Ruff format/check, and strict mypy pass.

### File List

- .github/workflows/quality.yml
- docs/contributing.md
- tests/unit/test_quality_configuration.py

## Change Log

- 2026-07-09: Added reproducible CI quality gates and contributor policy.
