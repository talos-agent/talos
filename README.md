# Talos

This repository contains the code for Talos, an AI agent for managing a cryptocurrency treasury, built with LangChain. The official documentation for the Talos project can be found at [docs.talos.is](https://docs.talos.is/).

Used LangChain to create a conversational agent with both research and onchain transaction execution capabilities. The agent is designed to be used by a DAO to manage its treasury, and can be used to perform tasks such as:

-   Researching and evaluating investment opportunities
-   Executing trades on decentralized exchanges
-   Providing reports on the treasury's performance

The agent is designed to be extensible, and can be customized to meet the specific needs of a DAO. For example, it can be configured to use different data sources, or to use different trading strategies. For more information on the governance and vault strategies, please see the [governance](https://docs.talos.is/governance) and [vault strategies](https://docs.talos.is/vault-strategies) pages on the official documentation.

## Directory Structure

The repository is structured as follows:

-   `.github/`: Contains GitHub Actions workflows for CI/CD.
-   `src/`: Contains the source code for the Talos agent.
    -   `crypto_sentiment/`: Contains a sub-package for sentiment analysis of cryptocurrencies.
    -   `talos/`: Contains the main source code for the Talos agent.
        -   `agent/`: Contains the core agent logic.
        -   `core/`: Contains the core components of the agent, such as the CLI and the main agent loop.
        -   `disciplines/`: Contains the different disciplines that the agent can perform, such as research and trading.
        -   `hypervisor/`: Contains the hypervisor for managing the agent's disciplines. The hypervisor is responsible for monitoring the agent's actions and ensuring that it doesn't do anything wrong. It will also be used to evaluate proposals, which are tracked at [https://github.com/talos-agent/TIPs](https://github.com/talos-agent/TIPs).
        -   `prompts/`: Contains the prompts used by the agent.
        -   `tools/`: Contains the tools that the agent can use, such as GitBook, GitHub, IPFS, and Twitter.
        -   `utils/`: Contains utility functions.
-   `tests/`: Contains the tests for the Talos agent.
-   `proposal_example.py`: An example of how to use the agent to evaluate a proposal.

## Key Components

Talos is comprised of several key components that allow it to function as a decentralized AI agent. These components are:

-   **Twitter:** Talos can interact with users on Twitter, allowing it to engage with the community and respond to inquiries.
-   **GitHub:** Talos can interact with GitHub, allowing it to review code, commit code, and manage its own codebase.
-   **GitBook:** Talos can interact with GitBook, allowing it to update its own documentation.
-   **Proposals:** Talos can manage its own treasury and key protocol actions through a proposal system.
-   **Hypervisor and Council:** The hypervisor and the council are responsible for protecting Talos from performing any nefarious actions.

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
uv run talos
```

You can then interact with the agent in a continuous conversation. To exit, type `exit`.

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
