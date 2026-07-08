import tomllib
from importlib import import_module
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[2]


def test_public_client_import() -> None:
    bcic = import_module("bcic")
    client_module = import_module("bcic.client")

    assert bcic.Client is client_module.Client
    assert bcic.__all__ == ["Client"]


def test_package_metadata_and_tooling_baseline() -> None:
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    project = pyproject["project"]
    dependencies = project["dependencies"]
    dev_dependencies = pyproject["tool"]["poetry"]["group"]["dev"]["dependencies"]

    assert project["requires-python"] == ">=3.12,<4.0"
    assert any(dependency.startswith("httpx") for dependency in dependencies)
    assert any(
        dependency.startswith("pydantic") and ">=2" in dependency and "<3" in dependency
        for dependency in dependencies
    )
    assert any(dependency.startswith("tenacity") for dependency in dependencies)
    assert {"pytest", "ruff", "mypy"} <= dev_dependencies.keys()
    assert pyproject["tool"]["pytest"]["ini_options"]["testpaths"] == ["tests/unit"]
    assert "ruff" in pyproject["tool"]
    assert "mypy" in pyproject["tool"]
