# Release Process

Releases are intentional maintainer operations. Do not change the package
version as part of unrelated feature work.

## Checklist

1. Classify changes using [versioning.md](versioning.md) and choose the version.
2. Update `CHANGELOG.md`: move relevant Unreleased entries to a dated version,
   retain all Added, Changed, Deprecated, Removed, Fixed, and Security headings,
   and add migration guidance for incompatible changes.
3. Update `pyproject.toml` and refresh/verify the lock:

   ```console
   poetry lock
   poetry lock --check
   ```

4. Confirm consumer docs, examples, API reference, and deprecation targets match
   the release.
5. Run all quality gates:

   ```console
   poetry run pytest
   poetry run ruff check .
   poetry run ruff format --check .
   poetry run mypy
   ```

6. Build and inspect distributions:

   ```console
   poetry build
   ```

7. Commit the version, lockfile, changelog, and documentation together. Tag the
   exact commit as `vX.Y.Z` only after review and green CI.
8. Publish from the reviewed tag using the approved package registry process,
   then verify installation and the published release notes.

Never publish with uncommitted changes, skipped gates, stale migration notes,
or credentials in repository/CI configuration.
