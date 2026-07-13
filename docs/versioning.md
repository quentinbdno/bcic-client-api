# Versioning and Compatibility

The project uses Semantic Versioning 2.0.0 after version 1.0. The package
version remains `0.1.0` until an actual release is prepared.

## Public API boundary

Compatibility promises cover:

- `bcic.Client`, its documented constructor, lifecycle, and endpoint properties
- documented methods on `client.records`, `client.users`, `client.binary`, and
  `client.methods`
- documented model names and fields exported from `bcic.models`
- documented exception names in `bcic.exceptions`

Leading-underscore names and modules, authentication/session state, transport,
parser, endpoint composition context, implementation helpers, and test seams
are internal. Documentation or examples that intentionally import a public
module make the named symbol part of the documented boundary; incidental
reachability does not.

## Pre-1.0 policy

Before 1.0, incompatible public changes may ship in a minor release. Every
public change must appear prominently in release notes. A breaking change must
include a **Migration guidance** section describing affected consumers, old
and new usage, and any behavior or data-shape impact. Patch releases must
remain backward compatible.

## Release decision table

| Change | Pre-1.0 | 1.0 and later |
| --- | --- | --- |
| Breaking endpoint, model, or exception change | Minor, prominently documented with migration guidance | Major |
| Compatible public API addition | Minor | Minor |
| Backward-compatible bug or security fix | Patch | Patch |
| Documentation/test/internal-only change | Patch when released | Patch |
| Public deprecation without removal | Minor | Minor |

## Deprecation and removal

After 1.0, public removal requires a documented replacement and
`DeprecationWarning` for at least one minor release before removal. The message
must name the deprecated API, replacement, and planned removal version. Warnings
must point to consumer code. `FutureWarning` is not used for developer-facing
API deprecations.

No current public API is deprecated merely to test this mechanism. The private
helper and private test callable validate the standard warning contract.
