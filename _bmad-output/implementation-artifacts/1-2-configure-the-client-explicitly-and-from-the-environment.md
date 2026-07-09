---
baseline_commit: 735639e6fedc09bcbbf016cecf1cfc1898558cfa
---

# Story 1.2: Configure the Client Explicitly and From the Environment

Status: done

## Story

As an SDK consumer,
I want to configure the client through explicit values or environment variables,
so that I can use the same SDK safely in local development, tests, and deployed automation.

## Acceptance Criteria

1. **Given** valid explicit configuration values for the base URL and authentication  
   **When** the developer creates a `Client`  
   **Then** the client accepts those values together with optional timeout, retry, and output settings  
   **And** configuration validation performs no network request.

2. **Given** required configuration is absent or invalid  
   **When** the developer creates a `Client`  
   **Then** creation fails with a typed SDK configuration exception  
   **And** the exception does not expose authentication secrets.

3. **Given** valid BCIC environment variables  
   **When** the developer constructs the client through the environment-based configuration path  
   **Then** the same validated client configuration is produced  
   **And** explicit overrides take precedence over environment values.

4. **Given** no dotenv integration is installed or enabled  
   **When** the `bcic` package is imported  
   **Then** the import succeeds without loading a dotenv file  
   **And** no environment or secret values are logged during import or configuration.

## Tasks / Subtasks

- [x] Define typed SDK configuration and configuration failure boundaries (AC: 1, 2)
  - [x] Create `bcic/config.py` with an immutable Pydantic 2 `ClientConfig`.
  - [x] Validate an HTTP(S) base URL, non-empty username/password, positive timeout, non-negative retry count/wait, and JSON/XML output format.
  - [x] Store passwords with `SecretStr`; ensure model repr and public exceptions do not reveal them.
  - [x] Create `bcic/exceptions.py` with minimal `BCICError` and `ConfigurationError` types; defer the full Epic 2 hierarchy.
- [x] Configure `Client` explicitly without side effects (AC: 1, 2)
  - [x] Add documented constructor parameters for base URL, username, password, timeout, retry settings, and output format.
  - [x] Expose the validated immutable configuration through `Client.config`.
  - [x] Wrap Pydantic validation failures as sanitized `ConfigurationError` without network, filesystem, dotenv, or logging side effects.
- [x] Add environment-based construction with deterministic precedence (AC: 3, 4)
  - [x] Implement `Client.from_env()` using `BCIC_BASE_URL`, `BCIC_USERNAME`, `BCIC_PASSWORD`, `BCIC_TIMEOUT`, `BCIC_MAX_RETRIES`, `BCIC_RETRY_WAIT_SECONDS`, and `BCIC_OUTPUT_FORMAT`.
  - [x] Accept an injectable mapping for deterministic tests; otherwise read `os.environ` only when `from_env()` is called.
  - [x] Let non-`None` explicit keyword overrides win over environment values.
  - [x] Do not add or import `python-dotenv`.
- [x] Add and run configuration tests and all quality gates (AC: 1–4)
  - [x] Cover explicit configuration, defaults, environment construction, precedence, and absence of network activity.
  - [x] Cover missing/invalid values and assert representative secrets are absent from repr and exception text.
  - [x] Verify importing `bcic` does not read environment variables or configure/emit logs.
  - [x] Run pytest, Ruff lint/format, strict mypy, and Poetry package checks.

### Review Findings

- [x] [Review][Patch] Reject malformed base URL authorities and ports [bcic/config.py:28]
- [x] [Review][Patch] Reject whitespace-only usernames and passwords [bcic/config.py:17]
- [x] [Review][Patch] Reject non-finite timeout and retry-wait values [bcic/config.py:19]
- [x] [Review][Patch] Reject booleans for the retry-count field [bcic/config.py:20]

## Dev Notes

### Developer Context and Guardrails

- Preserve Story 1.1's `from bcic import Client` contract and explicit `__all__ = ["Client"]`.
- `ClientConfig` is the single validated configuration contract. Both explicit and environment paths must construct it.
- Authentication behavior and session state remain deferred to Epic 2. This story stores credentials but performs no login, HTTP client construction, request, retry, logout, or transport work.
- Use only existing Pydantic 2 and standard-library facilities. `pydantic-settings` and `python-dotenv` would be new dependencies and are not required.
- `from_env()` is the only environment-reading boundary. Module import and direct construction must not inspect the environment.
- Never interpolate raw Pydantic validation input into `ConfigurationError`; use a stable sanitized message and exception chaining.
- Normalize the base URL to a plain string without a trailing slash so later transport URL composition has one canonical input.
- Output format is configuration-only here. Allow `json` and `xml` so Story 2 parsing can remain JSON-first while preserving the architecture's XML-compatible boundary.

### Architecture Compliance

- Update `bcic/client.py`; add `bcic/config.py`, `bcic/exceptions.py`, and `tests/unit/test_client.py`.
- Keep `bcic/__init__.py` unchanged unless needed to preserve its existing public export; configuration and exception types are internal module imports in this story.
- Follow AD-4 for a typed sanitized public failure boundary and AD-7 for dependency/configuration discipline.
- Do not add `auth.py`, `transport.py`, endpoint packages, models, docs, or examples.

### Testing Requirements

- Tests must be deterministic, offline, and use an injected environment mapping rather than mutating global environment where practical.
- Patch or guard network entry points when asserting that construction performs no I/O.
- Assert values and types on `Client.config`, including `SecretStr.get_secret_value()` only inside tests.
- Run the complete existing suite so Story 1.1 packaging/import behavior remains green.

### Previous Story Intelligence

- Story 1.1 established the flat `bcic/` layout, a minimal documented `Client`, centralized Poetry tooling, and strict mypy/Ruff gates.
- Poetry 2.4.1 generated the current lockfile; Pydantic 2.13.4 is resolved.
- The existing public export test expects exactly `["Client"]`; do not broaden top-level exports.

### Latest Technical Information

- Pydantic 2 models validate annotated fields at construction and support `ConfigDict`; use `extra="forbid"` and `frozen=True` for a strict immutable contract.
- Pydantic `SecretStr` masks values in repr/serialization by default, but SDK exceptions must still avoid including raw validation input.
- Pydantic URL types validate URL structure; convert the validated value to the canonical string stored by the SDK.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 1, Story 1.2]
- [Source: `_bmad-output/planning-artifacts/architecture/architecture-bcic-client-api-2026-07-08/ARCHITECTURE-SPINE.md` — AD-4, AD-7, Consistency Conventions, Capability Map]
- [Source: `_bmad-output/planning-artifacts/prds/prd-bcic-client-api-2026-07-08/prd.md` — FR-2, NFR-10, NFR-11, NFR-16–21]
- [Pydantic models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic network types](https://docs.pydantic.dev/latest/api/networks/)
- [Pydantic secret types](https://docs.pydantic.dev/latest/api/types/#pydantic.types.SecretStr)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- RED: configuration tests failed during collection because
  `bcic.exceptions` did not exist.

### Implementation Plan

- Establish the sanitized exception boundary and immutable validated
  configuration model, then make explicit and environment construction converge
  on the same `Client` initializer.
- Keep all construction offline and verify precedence, validation, secret
  redaction, and import compatibility before running the full quality suite.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added immutable Pydantic configuration with canonical URL handling, bounded
  retry/timeout values, output-format validation, and masked credentials.
- Added sanitized SDK configuration exceptions and explicit/environment client
  construction with deterministic non-`None` override precedence.
- Verified configuration performs no network, dotenv, filesystem, or logging
  work; all 14 tests and Poetry/Ruff/mypy gates pass.

### File List

- `bcic/client.py`
- `bcic/config.py`
- `bcic/exceptions.py`
- `tests/unit/test_client.py`
- `_bmad-output/implementation-artifacts/1-2-configure-the-client-explicitly-and-from-the-environment.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`

## Change Log

- 2026-07-08: Added validated explicit and environment-derived client
  configuration with sanitized failures.
