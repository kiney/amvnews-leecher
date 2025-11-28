Always read README.md before doing anything.

Write tests but don't overuse them.
You can use puppeteer to help scraper development.
When changing something that changes what the software does or how it works make sure to update documentation and tests.

## Python Setup

We use a venv in `.venv` and `uv` for Python package management.

The project uses modern `pyproject.toml` structure (PEP 621)

## Installing Dependencies

NEVER install anything without asking the user for approval.

When dependencies need to be added:
1. Add them to `pyproject.toml` under `[project.dependencies]` or `[project.optional-dependencies.dev]`
2. Tell the user to apply changes with: `uv pip install -e ".[dev]"`
