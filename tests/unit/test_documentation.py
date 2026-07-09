"""Lightweight consumer documentation validation."""

import re
from pathlib import Path

DOCS = Path(__file__).parents[2] / "docs"
REQUIRED = {
    "index.md",
    "installation.md",
    "quick-start.md",
    "authentication.md",
    "errors.md",
    "pagination.md",
    "api-reference.md",
}


def test_required_consumer_pages_exist_and_are_linked() -> None:
    assert REQUIRED <= {path.name for path in DOCS.glob("*.md")}
    index = (DOCS / "index.md").read_text(encoding="utf-8")
    links = set(re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", index))
    assert {name for name in REQUIRED if name != "index.md"} <= links


def test_relative_markdown_links_resolve() -> None:
    for page in DOCS.glob("*.md"):
        for target in re.findall(
            r"\[[^]]+\]\((?!https?://|#)([^)#]+\.md)(?:#[^)]+)?\)",
            page.read_text(encoding="utf-8"),
        ):
            assert (page.parent / target).is_file(), f"{page}: broken link {target}"


def test_python_documentation_blocks_compile() -> None:
    for page in DOCS.glob("*.md"):
        content = page.read_text(encoding="utf-8")
        for number, block in enumerate(
            re.findall(r"```python\n(.*?)```", content, re.DOTALL), start=1
        ):
            compile(block, f"{page}#python-{number}", "exec")
