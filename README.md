# Talos

An AI agent for managing a cryptocurrency treasury, built with LangChain.

This project uses LangChain to create a conversational agent with research capabilities.

## Tools

The project provides a set of tools for interacting with various services:

-   `gitbook`: A tool for interacting with GitBook.
-   `github`: A tool for interacting with GitHub.
-   `ipfs`: A tool for interacting with IPFS.
-   `twitter`: A tool for interacting with Twitter.

## Development

This project uses `uv` for dependency management.

1.  Install `uv`:
    ```bash
pip install talos
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
