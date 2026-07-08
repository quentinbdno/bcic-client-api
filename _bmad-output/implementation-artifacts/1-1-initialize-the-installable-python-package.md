---
baseline_commit: 735639e6fedc09bcbbf016cecf1cfc1898558cfa
---

# Story 1.1: Initialize the Installable Python Package

Status: review

## Story

As a Python developer,
I want to install and import the BCIC SDK,
so that I can begin integrating BCIC into an application using a conventional Python package.

## Acceptance Criteria

1. **Given** a supported Python 3.12 or later environment  
   **When** the developer installs the project through Poetry  
   **Then** the `bcic` package and its runtime dependencies are installed successfully  
   **And** the project declares `httpx`, Pydantic 2, and `tenacity` as runtime dependencies.

2. **Given** a development installation  
   **When** the maintainer installs the development dependency group  
   **Then** `pytest`, Ruff, and mypy are available  
   **And** their baseline configuration is defined in `pyproject.toml`.

3. **Given** the package is installed  
   **When** application code runs `from bcic import Client`  
   **Then** the import succeeds  
   **And** internal modules are not required as part of the primary public import path.

## Tasks / Subtasks

- [x] Create the Poetry package definition in root `pyproject.toml` (AC: 1, 2)
  - [x] Define package metadata and the `bcic` package using a Python constraint of `>=3.12,<4.0`.
  - [x] Declare runtime dependencies: `httpx`, `pydantic` constrained to `>=2,<3`, and `tenacity`.
  - [x] Declare `pytest`, `ruff`, and `mypy` in a development dependency group.
  - [x] Add baseline `[tool.ruff]`, `[tool.mypy]`, and pytest configuration; point pytest at `tests/unit`.
  - [x] Generate and commit `poetry.lock` with Poetry. Do not hand-author or fabricate it if Poetry is unavailable.
- [x] Establish the minimal public package surface (AC: 3)
  - [x] Create `bcic/__init__.py` and export only `Client` through an explicit `__all__`.
  - [x] Create `bcic/client.py` with the minimal documented `Client` type required for a stable import.
  - [x] Do not implement configuration, transport, authentication, endpoints, models, or network behavior in this story.
- [x] Add foundation tests under `tests/unit/` (AC: 1, 2, 3)
  - [x] Verify `from bcic import Client` succeeds and resolves to `bcic.client.Client`.
  - [x] Verify the intended top-level public export set; do not assert that Python makes internal modules technically inaccessible.
  - [x] Add a package-metadata test or equivalent check confirming Python support and required runtime/dev dependency declarations.
- [x] Validate the package and quality baseline (AC: 1, 2, 3)
  - [x] Run `poetry check`, `poetry install --with dev`, `poetry build`, and an import smoke test against the installed artifact.
  - [x] Run `poetry run pytest`, `poetry run ruff check .`, `poetry run ruff format --check .`, and `poetry run mypy bcic`.
  - [x] Confirm both wheel and source distribution are produced and contain the `bcic` package.

## Dev Notes

### Developer Context and Guardrails

- This is the first implementation story. The repository currently contains only `LICENSE`; every implementation file listed below is new.
- Keep this story to packaging, import surface, and baseline tool configuration. Stories 1.2–1.4 own configuration, endpoint composition, and common Pydantic models. Epic 2 owns authentication and transport.
- `Client` may be an intentionally minimal class, but it must be a real, documented type exported from `bcic.client`; do not hide an incomplete dependency graph behind import-time stubs.
- Imports must have no network, environment-loading, filesystem, logging-configuration, or other side effects.
- `bcic/__init__.py` is the consumer-facing boundary. Do not re-export `httpx`, Pydantic, Tenacity, transport internals, or placeholder endpoint types.
- Preserve the architecture's flat `bcic/` package layout. Do not introduce a `src/` layout without an explicit architecture change.
- Use `pyproject.toml` as the single configuration source. Do not add `setup.py`, `setup.cfg`, `requirements*.txt`, standalone Ruff/mypy configs, or a separate pytest config.
- Dependency constraints should express supported compatibility; `poetry.lock` records exact development/CI resolution. Avoid unbounded dependencies and avoid exact runtime pins in package metadata unless compatibility evidence requires them.
- The architecture explicitly says Poetry is not installed in the current workspace. At story creation time `poetry --version` fails, while Python 3.12.3 is available. Install/use an approved Poetry toolchain before generating the lockfile; never synthesize lock content.
- No live BCIC tenant, credentials, REST method inventory, XML support, REST v2 adapter, docs suite, or examples are in scope.

### Architecture Compliance

- Follow AD-1: the primary public entry point is `bcic.Client`.
- Follow AD-7: Poetry owns package metadata, dependencies, build settings, and centralized pytest/Ruff/mypy configuration; commit `poetry.lock`.
- Keep the package compatible with the structural seed. This story creates only:

```text
pyproject.toml
poetry.lock
bcic/
  __init__.py
  client.py
tests/
  unit/
    test_package.py
```

- Add no production dependency beyond `httpx`, Pydantic v2, and `tenacity`. `python-dotenv` is optional and belongs to Story 1.2 if selected.
- Baseline mypy configuration must type-check library code and baseline Ruff configuration must cover linting plus formatting. Tests must run without credentials or network access.

### Testing Requirements

- Test the installed-package contract, not only imports from the repository root. At minimum, build artifacts and smoke-test the wheel in an isolated environment or use an equivalent Poetry installation check.
- Keep tests deterministic and offline. This story has no HTTP behavior.
- Configure pytest through `pyproject.toml`. `[tool.pytest.ini_options]` is broadly supported and remains valid with current pytest; use native `[tool.pytest]` only if the selected pytest constraint is 9+.
- Acceptance is not complete if the lockfile, build, import smoke test, pytest, Ruff check/format check, or mypy fails.

### Latest Technical Information

- Poetry's current documentation describes deterministic dependency resolution and lockfile generation; use the installed Poetry CLI to create the lock rather than choosing transitive versions manually.
- HTTPX currently requires Python 3.9+, so the project's Python 3.12+ floor is compatible. Do not enable optional HTTP/2, CLI, compression, or proxy extras in this foundation story.
- Pydantic v1 is maintenance-only; constrain the project to Pydantic v2.
- Tenacity remains the selected general-purpose retry dependency, but retry behavior is deferred to Epic 2.

### Project Structure Notes

- No existing code files require preservation.
- The architecture seed includes many future modules. Creating empty placeholder modules now would blur story ownership and enlarge the public/internal surface without behavior; create them in the stories that define their contracts.
- The distribution/project name is `bcic-client-api`; the import package is `bcic`.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 1, Story 1.1]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-bcic-client-api-2026-07-08/ARCHITECTURE-SPINE.md` — AD-1, AD-7, Stack, Structural Seed]
- [Source: `_bmad-output/planning-artifacts/prds/prd-bcic-client-api-2026-07-08/prd.md` — FR-1, FR-2, §8.3, §9]
- [Poetry documentation](https://python-poetry.org/)
- [HTTPX documentation](https://www.python-httpx.org/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- [Tenacity documentation](https://tenacity.readthedocs.io/en/stable/)
- [pytest configuration documentation](https://docs.pytest.org/en/stable/reference/customize.html)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- RED: `python3 -m pytest tests/unit/test_package.py` failed because the
  development test dependency was not installed.

### Implementation Plan

- Define centralized Poetry/package/tool metadata, generate the lockfile with
  Poetry, then establish the minimal public import surface.
- Exercise metadata and public exports with deterministic unit tests before
  validating installation and built artifacts.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Defined Poetry 2 package metadata, bounded runtime/development dependencies,
  centralized pytest/Ruff/mypy configuration, and a Poetry-generated lockfile.
- Added the side-effect-free `bcic.Client` public import boundary with no
  configuration, transport, authentication, endpoint, or model behavior.
- Added deterministic metadata and public-surface tests; all 2 tests pass.
- Passed `poetry check`, locked development installation, wheel/sdist build,
  Ruff lint/format, strict mypy, and isolated installed-wheel import checks.
- Confirmed both distribution archives contain `bcic/__init__.py` and
  `bcic/client.py`.

### File List

- `pyproject.toml`
- `poetry.lock`
- `bcic/__init__.py`
- `bcic/client.py`
- `tests/unit/test_package.py`
- `_bmad-output/implementation-artifacts/1-1-initialize-the-installable-python-package.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-07-08: Initialized the installable Poetry package, minimal public
  `Client` surface, foundation tests, and quality baseline.
