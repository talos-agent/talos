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
from agent.models import AddDatasetParams, RunParams

# Initialize the agent
agent = HaystackAgent()

# Add data from a PDF
agent.add_dataset("path/to/your/document.pdf", params=AddDatasetParams())

# Add data from a website
agent.add_dataset("https://en.wikipedia.org/wiki/Artificial_intelligence", params=AddDatasetParams())

# Run a query
results = agent.run("What is artificial intelligence?", params=RunParams())
print(results)

# Run a query with web search
results = agent.run(
    "Who won the 2023 Nobel Prize in Physics?",
    params=RunParams(web_search=True),
)
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
