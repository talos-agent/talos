# Treasury Agent

An AI agent for managing a cryptocurrency treasury, built with Haystack.

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
    uv pip install -e .[core,dev]
    ```

## Usage

```python
from agent.haystack_agent import HaystackAgent

# Initialize the agent
agent = HaystackAgent()

# Add a dataset (e.g., SQuAD)
agent.add_dataset("squad")

# Run a query
results = agent.run("What is the capital of France?")
print(results)

# Run a query with web search
results = agent.run("Who won the 2023 Nobel Prize in Physics?", params={"web_search": True})
print(results)
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
