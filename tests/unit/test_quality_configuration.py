"""Repository-level quality gate configuration contracts."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]


def test_github_quality_workflow_runs_all_local_gates() -> None:
    workflow = PROJECT_ROOT / ".github/workflows/quality.yml"
    content = workflow.read_text(encoding="utf-8")

    assert "contents: read" in content
    assert 'python-version: ["3.12", "3.14"]' in content
    assert "poetry install" in content
    for command in (
        "poetry run pytest",
        "poetry run ruff check .",
        "poetry run ruff format --check .",
        "poetry run mypy",
    ):
        assert command in content


def test_contributor_guide_matches_ci_commands() -> None:
    content = (PROJECT_ROOT / "docs/contributing.md").read_text(encoding="utf-8")
    assert "Runtime dependencies" in content
    assert "Development dependencies" in content
    assert "poetry lock --check" in content
