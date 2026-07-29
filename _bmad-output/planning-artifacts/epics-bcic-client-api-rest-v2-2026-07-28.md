# BCIC Client API - REST v2 Implementation Roadmap

Note: A concrete implementation-ready backlog supersedes this high-level roadmap.
See: `_bmad-output/planning-artifacts/epics-bcic-client-api-rest-v2-readiness-2026-07-29.md`.

## Epic 1 - Versioned Client Foundation

Goal: expose an explicit version selector without breaking v1 consumers.

Stories:
- add `api_version`-driven client selection
- preserve current `Client` defaults and v1 behavior
- expose versioned endpoint access paths

## Epic 2 - REST v2 Transport and Auth

Goal: implement a transport/auth stack for v2 that does not reuse v1 request construction.

Stories:
- define v2 request builder and base transport
- implement v2 auth strategy
- map v2 errors into the shared exception hierarchy

## Epic 3 - REST v2 Models and Endpoints

Goal: add versioned domain models and the first v2 endpoint set.

Stories:
- define v2 request/response models
- implement core v2 endpoints
- add version-aware pagination helpers where needed

## Epic 4 - Compatibility and Migration Guardrails

Goal: make mixed-version support safe to maintain.

Stories:
- add tests proving v1 backward compatibility
- add tests proving v2 isolation
- document migration rules and version-selection examples

## Epic 5 - Documentation and Release Readiness

Goal: give consumers and maintainers enough guidance to adopt v2 confidently.

Stories:
- update user docs with v1/v2 comparison
- add code examples for both versions
- publish versioning, compatibility, and deprecation guidance

