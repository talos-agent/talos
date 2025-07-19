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
*   Use type hints for all function signatures.
*   Write clear and concise docstrings for all modules, classes, and functions.
*   Keep lines under 88 characters long.

## General Guidance

*   Write clear and descriptive commit messages.
*   Break down large changes into smaller, logical commits.
*   Ensure that all new code is covered by tests.
*   Update the documentation as needed.

## Commands

- `./run_checks.sh`: Run ruff, mypy, and pytest.
