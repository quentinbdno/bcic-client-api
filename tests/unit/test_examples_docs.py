"""Runnable-example and public-docstring contracts."""

import ast
import importlib.util
import inspect
from pathlib import Path

from bcic import Client
from bcic.endpoints import (
    BinaryEndpoint,
    MethodsEndpoint,
    RecordsEndpoint,
    UsersEndpoint,
)
from bcic.exceptions import BCICError
from bcic.models.common import SDKModel

ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "examples"
REQUIRED_EXAMPLES = {
    "authentication.py",
    "records.py",
    "pagination.py",
    "permissions.py",
    "binary.py",
    "error_handling.py",
}
FORBIDDEN_MARKERS = ("password-marker", "session-marker", "token-marker", "BEGIN ")


def test_examples_compile_import_safely_and_use_main_guards() -> None:
    assert REQUIRED_EXAMPLES <= {path.name for path in EXAMPLES.glob("*.py")}
    for path in EXAMPLES.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        assert any(
            isinstance(node, ast.FunctionDef) and node.name == "main"
            for node in tree.body
        )
        assert 'if __name__ == "__main__":' in source
        assert all(marker not in source for marker in FORBIDDEN_MARKERS)
        spec = importlib.util.spec_from_file_location(f"example_{path.stem}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)


def test_public_classes_and_methods_have_docstrings() -> None:
    classes = (
        Client,
        RecordsEndpoint,
        UsersEndpoint,
        BinaryEndpoint,
        MethodsEndpoint,
        SDKModel,
        BCICError,
    )
    for cls in classes:
        assert inspect.getdoc(cls), cls.__qualname__
        for name, member in cls.__dict__.items():
            if not name.startswith("_"):
                target = member.fget if isinstance(member, property) else member
                if callable(target):
                    assert inspect.getdoc(target), f"{cls.__qualname__}.{name}"
