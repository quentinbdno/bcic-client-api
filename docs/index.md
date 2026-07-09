# BCIC Python SDK

The SDK provides typed, synchronous access to BCIC REST v1. Start with the
domain endpoints (`client.records`, `client.users`, and `client.binary`);
`client.methods` is a controlled lower-level escape hatch for documented REST
methods that do not yet have a domain API.

- [Installation](installation.md)
- [Quick start](quick-start.md)
- [Authentication and lifecycle](authentication.md)
- [Errors](errors.md)
- [Pagination](pagination.md)
- [API reference](api-reference.md)
- [Versioning and compatibility](versioning.md)
- [Release process](releasing.md)
- [Contributor setup](contributing.md)
- [Test coverage](testing.md)

The current implementation is JSON-first. Configuration includes an output
format boundary for future formats, but documented domain operations should
use the default JSON format.
