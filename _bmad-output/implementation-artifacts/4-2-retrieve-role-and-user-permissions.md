---
baseline_commit: b1f383f1fc11ad0e3d50214a46df2b647f37a06d
---

# Story 4.2: Retrieve Role and User Permissions

Status: review

## Story

As an SDK consumer,
I want to retrieve permissions assigned through a role or user,
so that automation can evaluate BCIC access using typed data.

## Acceptance Criteria

1. `client.users.get_permissions_by_role(role_id, entity_type, *, object_id=None, application_id=None)` validates dependent parameters, calls `getPermissionsByRole`, and returns `list[Permission]`.
2. `client.users.get_permissions_by_user(user_id, entity_type, *, object_id=None, application_id=None)` applies the user-specific entity rules, calls `getPermissionsByUser`, and returns the same `Permission` shape.
3. `Permission` preserves entity name/IDs and a deliberate mapping of permission names to `true`, `false`, or `conditional`; malformed or unknown permission values invalidate the whole result.
4. Invalid inputs send no request; denied, unsupported, missing-subject, and malformed responses raise sanitized `AuthorizationError`, `ValidationError`, `NotFoundError`, or `APIError` as appropriate.

## Tasks / Subtasks

- [x] Define typed permission query and response models (AC: 1-4)
  - [x] Add `PermissionEntityType`, subject-specific allowed entity sets, and conditional `object_id`/`application_id` validation
  - [x] Normalize stable identity keys separately from dynamic permission-name keys and validate values atomically
- [x] Implement role/user permission methods through shared transport (AC: 1-4)
  - [x] Map SDK names to `roleId`/`userId`, `entityType`, optional `objId`/`appId`, and configured output
  - [x] Reuse one private execution/normalization path while retaining the different role/user validation rules
- [x] Add unit tests and run all quality gates (AC: 1-4)
  - [x] Cover every entity-type dependency, role/user differences, valid conditional field permission, empty list, malformed item, and mapped failures
  - [x] Run pytest, Ruff format/check, and strict mypy

## Dev Notes

### Technical Requirements

- Extend `bcic/models/users.py` and `UsersEndpoint`; do not introduce a separate permissions endpoint.
- Role entity types: `field`, `object`, `application`, `menu`, `view`, `action`, `report`, `chart`. User permissions exclude `field`.
- Require `object_id` for role `field` and for both subjects' `view`, `action`, `report`, or `chart`; require `application_id` for `menu`; reject irrelevant extra IDs to prevent ambiguous requests.
- Both methods are GET and require full administrative privileges. Role IDs are original IDs; user IDs are documented user IDs.
- Response objects contain `name`, `id`, `originalId`, plus entity-dependent permission keys. Normalize permission keys without hard-coding one entity's verbs; restrict values to documented `true`, `false`, and role-field `conditional`.
- Do not silently coerce unknown strings, omit malformed items, or return partial collections.

### Architecture Compliance

- AD-1/AD-2: public domain methods delegate method execution.
- AD-4/AD-5: SDK-only exceptions and typed permission models with a deliberate dynamic mapping.
- AD-8: table-driven unit tests cover the validation matrix without live calls.

### Current State and Preservation

- Story 4.1 introduces `Role`, array-response support, and users endpoint request patterns. Reuse its identifier and collection normalization helpers.
- Preserve existing transport retry behavior: authorization/validation failures are terminal, while mapped transient failures remain retryable.

### File Structure and Testing

- UPDATE: `bcic/models/users.py`, `bcic/models/__init__.py`, `bcic/endpoints/users.py`, `tests/unit/test_endpoints_users.py`.
- No transport change should be needed beyond Story 4.1 array support.
- Test exact query parameter omission/inclusion and verify invalid dependency combinations produce zero requests.

### Previous Story Intelligence

- Story 4.1 establishes the typed user-domain model and top-level array parser contract. Do not create a second collection parser.
- No implementation completion notes exist while 4.1 remains ready-for-dev.

### References

- [Source: `_bmad-output/planning-artifacts/epics.md` — Epic 4, Story 4.2]
- [Source: architecture spine — AD-1, AD-2, AD-4, AD-5, AD-8]
- [Official REST v1 `getPermissionsByRole`](https://documentation.infiniteblue.com/platform/getPermissionsByRole.htm)
- [Official REST v1 `getPermissionsByUser`](https://documentation.infiniteblue.com/platform/getPermissionsByUser.htm)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

- Permission validation matrix and atomic response tests passed.
- Full suite and static quality gates passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added typed permission entities, dependency validation, and dynamic value normalization.
- Added shared role/user permission execution with subject-specific rules.

### File List

- bcic/endpoints/users.py
- bcic/models/__init__.py
- bcic/models/users.py
- tests/unit/test_endpoints_users.py

### Change Log

- 2026-07-09: Implemented typed role/user permission retrieval; status set to review.
