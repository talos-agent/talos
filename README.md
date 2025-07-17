# Treasury Agent

An AI agent for managing a cryptocurrency treasury, built with LangChain.

This project uses LangChain to create a conversational agent with research capabilities.

## Architecture

The project is divided into two main modules:

-   `conversational`: Contains the LangChain-based agent for managing conversations.
-   `research`: Contains the LangChain-based agent for performing research tasks.

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

### Interactive CLI

To start the interactive CLI, run the following command:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export PINATA_API_KEY="your-pinata-api-key"
export PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
treasury-agent
```

You can then interact with the agent in a continuous conversation. To exit, type `exit`.

You can also use the `ipfs` command to interact with IPFS:

-   `ipfs publish <file_path>`: Publishes a file to IPFS.
-   `ipfs read <ipfs_hash>`: Reads a file from IPFS.

### Proposal Evaluation Example

To run the proposal evaluation example, run the following command:

```bash
export OPENAI_API_KEY="your-openai-api-key"
python proposal_example.py
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
