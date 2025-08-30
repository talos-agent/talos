# Talos: An AI Protocol Owner

Welcome to Talos, an AI agent designed to act as an autonomous owner for decentralized protocols. Talos is not just a chatbot; it is a sophisticated AI system that can manage and govern a protocol, ensuring its integrity and security.

!!! info "Official Documentation"
    The official documentation for the Talos project can be found at [docs.talos.is](https://docs.talos.is/).

## What is Talos?

Talos is an AI agent that can:

- **Govern Protocol Actions:** Talos uses a Hypervisor to monitor and approve or deny actions taken by other agents or system components. This ensures that all actions align with the protocol's rules and objectives.
- **Evaluate Governance Proposals:** Talos can analyze and provide recommendations on governance proposals, considering their potential benefits, risks, and community feedback.
- **Interact with the Community:** Talos can engage with the community on platforms like Twitter to provide updates, answer questions, and gather feedback.
- **Manage its Own Codebase:** Talos can interact with GitHub to manage its own source code, including reviewing and committing changes.
- **Update Documentation:** Talos can update its own documentation on GitBook to ensure it remains accurate and up-to-date.

## Key Features

### Autonomous Treasury Management
Talos continuously monitors volatility, yield curves, and risk surfaces to compute optimal capital paths. Each strategy proposal must first be approved by the council, then deployed through ERC-4626 vaults spanning sophisticated LP positions to simple ETH lending.

### Governance & Security
The Hypervisor system ensures all actions are monitored and approved based on predefined rules and agent history, protecting the protocol from malicious or erroneous actions.

### Community Engagement
Talos can engage with the community on social platforms, providing updates, answering questions, and gathering feedback to inform protocol decisions.

## Quick Links

- [Getting Started](getting-started/overview.md) - Learn how to install and use Talos
- [Architecture](architecture/components.md) - Understand the core components and design
- [CLI Reference](cli/overview.md) - Complete command-line interface documentation
- [Development](development/contributing.md) - Contributing guidelines and development setup

## Repository Structure

The repository is organized as follows:

- `.github/` - GitHub Actions workflows for CI/CD
- `src/talos/` - Main source code for the Talos agent
  - `core/` - Core components (CLI, main agent loop)
  - `hypervisor/` - Hypervisor and Supervisor components
  - `services/` - Different services (proposal evaluation, etc.)
  - `prompts/` - Agent prompts and templates
  - `tools/` - External integrations (GitHub, Twitter, IPFS)
- `tests/` - Test suite
- `docs/` - Documentation source files
