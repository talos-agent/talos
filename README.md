# Treasury Agent

An AI agent for managing a cryptocurrency treasury.

## Development

This project uses `uv` for dependency management.

1.  Install `uv`:
    ```bash
    pip install uv
    ```
2.  Create a virtual environment:
    ```bash
    uv venv
    ```
3.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
4.  Install dependencies:
    ```bash
    uv pip install -e .[dev]
    ```

## Usage

```bash
treasury-agent
```

## Testing

```bash
pytest
```

## Linting and Type Checking

```bash
ruff check .
ty check .
```
