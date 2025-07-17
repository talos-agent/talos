# Treasury Agent

An AI agent for managing a cryptocurrency treasury, built with Haystack and Letta.

This project combines the strengths of two powerful AI frameworks:

-   **Letta**: For conversational AI and long-term memory.
-   **Haystack**: For deep research and question answering.

## Architecture

The project is divided into two main modules:

-   `conversational`: Contains the Letta-based agent for managing conversations.
-   `research`: Contains the Haystack-based agent for performing research tasks.

A top-level `MainAgent` delegates to the appropriate agent based on the user's query.

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
import os
from conversational.main_agent import MainAgent
from research.models import AddDatasetParams, RunParams

# Initialize the main agent
agent = MainAgent(
    letta_api_key=os.environ["LETTA_API_KEY"],
    letta_agent_id=os.environ["LETTA_AGENT_ID"],
)

# Add a dataset to the research agent
agent.add_dataset(
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    params=AddDatasetParams(),
)

# Have a conversation with the Letta agent
response = agent.run("Hello, how are you?", params=RunParams())
print(response)

# Perform a research query with the Haystack agent
response = agent.run("What is the capital of France?", params=RunParams())
print(response)

# Perform a research query with web search
response = agent.run(
    "Who won the 2023 Nobel Prize in Physics?",
    params=RunParams(web_search=True),
)
print(response)
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
