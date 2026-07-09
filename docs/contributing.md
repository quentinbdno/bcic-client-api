# Contributing

## Setup

Install Python 3.12 or newer and
[Poetry](https://python-poetry.org/docs/#installation), then create the locked
development environment:

```console
poetry install
poetry lock --check
```

`pyproject.toml` is the only dependency and tool-configuration source of truth;
commit the corresponding `poetry.lock` whenever dependency constraints change.

## Quality gates

Run the same four gates used by CI:

```console
poetry run pytest
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy
```

Tests require no BCIC tenant, credentials, or other secrets. The unit-test
configuration blocks live HTTP traffic.

## Dependency policy

Runtime dependencies belong in `[project].dependencies` only when SDK code
needs them in consumer installations. Development dependencies belong in
`[tool.poetry.group.dev.dependencies]` when they support testing, linting,
formatting, or static analysis.

Every addition requires an SDK-level rationale. Do not add convenience-only
packages, duplicate dependency managers, task runners, coverage services, or
test frameworks when the existing stack can meet the requirement.
