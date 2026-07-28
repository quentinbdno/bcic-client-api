# BCIC Client API - REST v2 Enablement PRD

## Overview

`bcic-client-api` is an existing Python SDK for BCIC REST v1. BCIC REST v2 now exists with a different contract, and the SDK must evolve without breaking the current v1 public API.

This PRD defines the product intent for a dual-version SDK:

- preserve existing v1 behavior and imports
- add a dedicated v2 surface rather than mixing v1 and v2 logic in one business layer
- make API version selection explicit through `api_version` or an equivalent transport selection mechanism
- use the official REST v2 documentation as the source of truth for endpoint shapes, auth, payloads, and response contracts

## Problem Statement

The current SDK is optimized around REST v1 method-style calls. REST v2 introduces different resource paths, request semantics, and likely different response shapes. If both versions are handled in a single transport and endpoint layer, the SDK will become harder to maintain, harder to test, and easier to break accidentally.

## Goals

1. Preserve v1 compatibility for all existing consumers.
2. Introduce a clean REST v2 implementation path that is explicit and isolated.
3. Keep shared concerns shared: configuration, HTTP client lifecycle, logging, retries, and base exception hierarchy.
4. Keep version-specific concerns separate: endpoint paths, request/response models, auth details if they differ, and parsing rules.
5. Produce documentation that lets maintainers and consumers understand which API they are using and why.

## Non-Goals

- Do not merge v1 and v2 contracts into a single generic domain layer.
- Do not silently auto-detect API version from the tenant or response headers.
- Do not break the v1 public API surface in the name of modernization.
- Do not assume v2 endpoint parity with v1 until verified against the official docs.

## Compatibility Analysis

### What Can Stay Shared

- package metadata and distribution workflow
- `Client` top-level entry point, if versioned sub-clients are exposed behind it
- config parsing and validation primitives
- HTTP client ownership and lifecycle management
- retry policy framework
- base SDK exception hierarchy
- logging policy and secret redaction
- common pagination helpers where the underlying API semantics are equivalent
- test fixtures for HTTP mocking and configuration validation

### What Should Become Version-Specific

- endpoint registry and path templates
- transport request builders
- authentication wiring if v2 differs from v1
- parser/normalizer logic
- response models and domain models
- paging semantics if v2 pages differ from v1
- error mapping if v2 returns different status envelopes

### Main Compatibility Risks

- v2 may use resource-oriented paths instead of v1 method-style endpoints.
- v2 may require different auth headers or token exchange behavior.
- v2 may return structurally different envelopes, so existing v1 models may not fit.
- v2 pagination may not map cleanly to v1 `list_all()` traversal.
- any attempt to “unify” endpoint code too early may create hidden coupling and regressions.

## Product Direction

The SDK should expose a deliberate version boundary:

- `Client(api_version="v1")` keeps today’s behavior.
- `Client(api_version="v2")` or `client.v2` activates the new REST v2 surface.
- v1 and v2 should each own their own endpoint set and typed models.
- shared infra should sit below both surfaces, not between them.

## Success Criteria

- Existing v1 consumers continue to work unchanged.
- A v2 consumer can use the SDK without importing or depending on v1 endpoint contracts.
- Maintainters can identify the version boundary in code and docs within minutes.
- Unit tests cover both surfaces with isolated fixtures.
- The documentation clearly states what is shared and what is version-specific.

## Open Questions

1. Does REST v2 require different authentication than v1?
2. Which v2 resources are in scope for the first release?
3. Should the public API prefer `client.v2` or `Client(api_version="v2")` as the primary discoverable entry?
4. Are v1 and v2 expected to coexist indefinitely, or is v2 a future replacement?

