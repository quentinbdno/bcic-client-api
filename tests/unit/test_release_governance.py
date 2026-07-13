"""Release-governance and private deprecation mechanism contracts."""

import warnings
from pathlib import Path

from bcic._deprecation import warn_deprecated

ROOT = Path(__file__).parents[2]


def _private_legacy_callable() -> None:
    warn_deprecated(
        "_private_legacy_callable",
        replacement="_private_replacement",
        removal="1.3",
    )


def test_private_deprecation_helper_uses_standard_actionable_warning() -> None:
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        _private_legacy_callable()

    assert len(captured) == 1
    warning = captured[0]
    assert warning.category is DeprecationWarning
    assert "_private_legacy_callable is deprecated" in str(warning.message)
    assert "use _private_replacement instead" in str(warning.message)
    assert "removal in 1.3" in str(warning.message)
    assert warning.filename == __file__
    assert warning.lineno == 22


def test_release_artifacts_define_required_sections() -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    for heading in ("Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"):
        assert f"### {heading}" in changelog

    versioning = (ROOT / "docs/versioning.md").read_text(encoding="utf-8")
    releasing = (ROOT / "docs/releasing.md").read_text(encoding="utf-8")
    assert "Pre-1.0" in versioning
    assert "at least one minor release" in versioning
    assert "Migration guidance" in versioning
    assert "poetry run pytest" in releasing
    assert "poetry build" in releasing
