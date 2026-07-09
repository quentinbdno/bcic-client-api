# Public API Reference

Only documented public names are compatibility-facing. Leading-underscore
symbols and auth/transport composition internals are not consumer APIs.

## Client

`bcic.Client(*, base_url, username, password, timeout=30.0, max_retries=3,
retry_wait_seconds=0.5, output_format="json")`

- `Client.from_env(environ=None, **overrides) -> Client`
- `authenticate() -> None`, `logout() -> None`, `close() -> None`
- context manager support
- properties: `config`, `records`, `users`, `binary`, `methods`

## Record endpoint

- `records.get(object_name, record_id, *, field_names=None, composite=0)
  -> DynamicRecord`
- `records.get_page(view_id, *, start_row=0, page_size=100, composite=0,
  object_names=None, field_names=None, equality_filter=None,
  only_view_fields=False) -> Page[DynamicRecord]`
- `records.list_all(view_id, *, page_size=100, max_pages=100,
  max_items=10000, composite=0, object_names=None, field_names=None,
  equality_filter=None, only_view_fields=False) -> list[DynamicRecord]`
- `records.create(object_name, fields, *, use_ids=False)
  -> RecordCreationResult`
- `records.update(object_name, record_id, changes, *, use_ids=False)
  -> RecordUpdateResult`
- `records.delete(object_name, record_id) -> RecordDeletionResult`

## User and permission endpoint

- `users.list_roles() -> list[Role]`
- `users.get_role(role_id) -> Role` (the BCIC original role ID)
- `users.get_permissions_by_role(role_id, entity_type, *, object_id=None,
  application_id=None) -> list[Permission]`
- `users.get_permissions_by_user(user_id, entity_type, *, object_id=None,
  application_id=None) -> list[Permission]`

`PermissionEntityType` defines supported entity values. Some types require
`object_id` or `application_id`; invalid combinations raise `ValidationError`.

## Binary endpoint

- `binary.get(object_name, record_id, field_name, *, max_bytes=10485760)
  -> BinaryData`
- `binary.set(object_name, record_id, field_name, content, *, file_name,
  content_type, max_bytes=10485760) -> BinaryUploadResult`

Binary operations buffer complete payloads and enforce the configured decoded
size limit. Bytes and Base64 data are excluded from normal representations and
logs.

## Lower-level method endpoint

`methods.execute(method_name, parameters=None, *, http_method="GET",
output_format=None) -> dict[str, JSONValue]`

Prefer domain endpoints. This escape hatch still applies validation,
authentication, retries, parsing, logging, and exception mapping; it does not
make arbitrary URLs or unsafe method names available.

## Models and exceptions

Public typed models are exported from `bcic.models`: common `Page`,
`PageMetadata`, and `ResponseMetadata`; record request/result models and
`DynamicRecord`; `Role`, `Permission`, and `PermissionEntityType`; and binary
metadata/data/result models.

The exception hierarchy is documented in [Errors](errors.md). Pagination
behavior and `EqualityFilter` are documented in [Pagination](pagination.md).
Compatibility guarantees and deprecation rules are documented in
[Versioning](versioning.md).
