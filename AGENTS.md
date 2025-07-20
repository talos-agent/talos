# Agent Guidelines

This document provides general guidance for agents committing to this repository.

## Pre-commit Checks

Before committing any changes, please ensure that you run the following checks:

1.  **Ruff:** Run `ruff` to lint and format the code.
2.  **Mypy:** Run `mypy` to check for type errors.
3.  **Pytest:** Run `pytest` to ensure all tests pass.

## Code Style

Please adhere to the following code style guidelines:

*   Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for all Python code.
*   Use modern Python type hints (e.g., `list` and `dict` instead of `List` and `Dict`).
*   Never use quotes around type hints (e.g., `def foo() -> "MyClass": ...`). You can always add `from __future__ import annotations` to the top of the file if you need to delay the evaluation of type hints.
*   Use type hints for all function signatures.
*   Write clear and concise docstrings for all modules, classes, and functions.
*   Keep lines under 88 characters long.
*   When creating Pydantic `BaseModel`s, use `model_post_init` for any post-initialization logic instead of overriding the `__init__` method.

## General Guidance

*   The default model for this project is `gpt-4o`.
*   Write clear and descriptive commit messages.
*   Break down large changes into smaller, logical commits.
*   Ensure that all new code is covered by tests.
*   Update the documentation as needed.

## Commands

- `./run_checks.sh`: Run ruff, mypy, and pytest.
