# Talos: An AI Protocol Owner

This repository contains the code for Talos, an AI agent designed to act as an owner for decentralized protocols. Talos is not just a chatbot; it is a sophisticated AI system that can manage and govern a protocol, ensuring its integrity and security.

The official documentation for the Talos project can be found at [docs.talos.is](https://docs.talos.is/).

## What is Talos?

Talos is an AI agent that can:

-   **Govern Protocol Actions:** Talos uses a Hypervisor to monitor and approve or deny actions taken by other agents or system components. This ensures that all actions align with the protocol's rules and objectives.
-   **Evaluate Governance Proposals:** Talos can analyze and provide recommendations on governance proposals, considering their potential benefits, risks, and community feedback.
-   **Interact with the Community:** Talos can engage with the community on platforms like Twitter to provide updates, answer questions, and gather feedback.
-   **Manage its Own Codebase:** Talos can interact with GitHub to manage its own source code, including reviewing and committing changes.
-   **Update Documentation:** Talos can update its own documentation on GitBook to ensure it remains accurate and up-to-date.

## Directory Structure

The repository is structured as follows:

-   `.github/`: Contains GitHub Actions workflows for CI/CD.
-   `src/`: Contains the source code for the Talos agent.
    -   `talos/`: Contains the main source code for the Talos agent.
        -   `core/`: Contains the core components of the agent, such as the CLI and the main agent loop.
        -   `hypervisor/`: Contains the Hypervisor and Supervisor components, which are responsible for overseeing the agent's actions.
        -   `services/`: Contains the different services that the agent can perform, such as evaluating proposals.
        -   `prompts/`: Contains the prompts used by the agent.
        -   `tools/`: Contains the tools that the agent can use, such as GitBook, GitHub, IPFS, and Twitter.
-   `tests/`: Contains the tests for the Talos agent.
-   `proposal_example.py`: An example of how to use the agent to evaluate a proposal.

## Key Components

Talos is comprised of several key components that allow it to function as a decentralized AI protocol owner:

-   **Hypervisor and Supervisor:** The Hypervisor is the core of Talos's governance capabilities. It monitors all actions and uses a Supervisor to approve or deny them based on a set of rules and the agent's history. This protects the protocol from malicious or erroneous actions.
-   **Proposal Evaluation System:** Talos can systematically evaluate governance proposals, providing a detailed analysis to help stakeholders make informed decisions.
-   **Tool-Based Architecture:** Talos uses a variety of tools to interact with external services like Twitter, GitHub, and GitBook, allowing it to perform a wide range of tasks.

## Services

Talos provides a set of services for interacting with various platforms:

-   **Twitter:** Talos can use its Twitter service to post tweets, reply to mentions, and monitor conversations, allowing it to engage with the community and stay informed about the latest developments.
-   **GitHub:** The GitHub service enables Talos to interact with repositories, manage issues, and review and commit code. This allows Talos to autonomously manage its own codebase and contribute to other projects.
-   **GitBook:** With the GitBook service, Talos can create, edit, and manage documentation. This ensures that the project's documentation is always up-to-date.

## Development

This project uses `uv` for dependency management.

1.  Create a virtual environment:

    ```bash
    uv venv
    ```

2.  Activate the virtual environment:

    ```bash
    source .venv/bin/activate
    ```

3.  Install dependencies:

    ```bash
    ./scripts/install_deps.sh
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

### Daemon Mode

To run the agent in daemon mode for continuous operation with scheduled jobs:

```bash
export OPENAI_API_KEY="your-openai-api-key"
export GITHUB_API_TOKEN="your-github-token"
export TWITTER_BEARER_TOKEN="your-twitter-bearer-token"
export PINATA_API_KEY="your-pinata-api-key"
export PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
uv run talos daemon
```

The daemon will run continuously, executing scheduled jobs and can be gracefully shutdown with SIGTERM or SIGINT.

### Docker Usage

#### Building and Running with Docker

1. Build the Docker image:
   ```bash
   docker build -t talos-agent .
   ```

2. Run the container with environment variables:
   ```bash
   docker run -d \
     -e OPENAI_API_KEY="your-openai-api-key" \
     -e GITHUB_API_TOKEN="your-github-token" \
     -e TWITTER_BEARER_TOKEN="your-twitter-bearer-token" \
     -e PINATA_API_KEY="your-pinata-api-key" \
     -e PINATA_SECRET_API_KEY="your-pinata-secret-api-key" \
     --name talos-agent \
     talos-agent
   ```

3. View logs:
   ```bash
   docker logs -f talos-agent
   ```

4. Graceful shutdown:
   ```bash
   docker stop talos-agent
   ```

#### Using Docker Compose

1. Create a `.env` file with your API keys:
   ```bash
   OPENAI_API_KEY=your-openai-api-key
   GITHUB_API_TOKEN=your-github-token
   TWITTER_BEARER_TOKEN=your-twitter-bearer-token
   PINATA_API_KEY=your-pinata-api-key
   PINATA_SECRET_API_KEY=your-pinata-secret-api-key
   ```

2. Start the service:
   ```bash
   docker-compose up -d
   ```

3. View logs:
   ```bash
   docker-compose logs -f
   ```

4. Stop the service:
   ```bash
   docker-compose down
   ```

#### Required Environment Variables

- `OPENAI_API_KEY`: Required for AI functionality
- `GITHUB_API_TOKEN`: Required for GitHub operations
- `TWITTER_BEARER_TOKEN`: Required for Twitter functionality
- `PINATA_API_KEY`: Required for IPFS operations
- `PINATA_SECRET_API_KEY`: Required for IPFS operations

#### Graceful Shutdown

The Docker container supports graceful shutdown. When you run `docker stop`, it sends a SIGTERM signal to the process, which triggers:

1. Stopping the job scheduler
2. Completing any running jobs
3. Clean shutdown of all services

The container will wait up to 10 seconds for graceful shutdown before forcing termination.

### Proposal Evaluation Example

To run the proposal evaluation example, run the following command:

```bash
export OPENAI_API_key="<OPENAI_API_KEY>"
python proposal_example.py
```

## Testing, Linting and Type Checking

To run the test suite, lint, and type-check the code, run the following command:

```bash
./scripts/run_checks.sh
```
