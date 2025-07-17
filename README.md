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

To start the interactive CLI, run the following command:

```bash
export LETTA_API_KEY="your-letta-api-key"
export LETTA_AGENT_ID="your-letta-agent-id"
treasury-agent
```

You can then interact with the agent in a continuous conversation. To exit, type `exit`.

## Testing

```bash
pytest
```

## Linting and Type Checking

```bash
ruff check .
ty check .
```
