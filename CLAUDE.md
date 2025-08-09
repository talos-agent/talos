# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup and Dependencies
- `uv venv` - Create virtual environment
- `source .venv/bin/activate` - Activate virtual environment  
- `./scripts/install_deps.sh` - Install dependencies
- `uv pip install -e .[dev]` - Install project in development mode with dev dependencies

### Code Quality and Testing
- `./scripts/run_checks.sh` - Run complete test suite (ruff format, ruff check, mypy, pytest)
- `uv run ruff format .` - Format code
- `uv run ruff check .` - Lint code
- `uv run mypy src` - Type check source code
- `uv run pytest` - Run all tests
- `uv run pytest tests/test_specific.py` - Run specific test file
- `uv run isort .` - Sort imports

### Running the Application
- `uv run talos` - Start interactive CLI (requires OPENAI_API_KEY, PINATA_API_KEY, PINATA_SECRET_API_KEY environment variables)
- `uv run talos proposals eval --file <path>` - Evaluate a proposal from file
- `uv run talos twitter get-user-prompt <username>` - Get Twitter user persona prompt

## Architecture Overview

Talos is an AI protocol owner system built with a sophisticated multi-agent architecture:

### Core Components

**MainAgent** (`src/talos/core/main_agent.py`): The top-level orchestrating agent that:
- Delegates tasks using a Router to different services and skills
- Manages scheduled jobs for autonomous execution
- Integrates with Hypervisor for action approval
- Handles dataset management for contextual information retrieval

**Agent Base Class** (`src/talos/core/agent.py`): Foundation for all agents providing:
- LangChain integration with chat models
- Message history management and memory persistence  
- Tool management and supervised tool execution
- Context building with dataset search integration

**Hypervisor** (`src/talos/hypervisor/hypervisor.py`): Security and governance layer that:
- Monitors and approves/denies agent actions
- Uses dedicated prompts to evaluate action safety
- Maintains agent history for context-aware decisions

### Key Architectural Patterns

**Router Pattern** (`src/talos/core/router.py`): Delegates tasks to appropriate services and skills based on request classification.

**Skill-based Architecture** (`src/talos/skills/`): Modular capabilities including:
- ProposalsSkill - Governance proposal evaluation
- TwitterSentimentSkill - Social media sentiment analysis  
- CryptographySkill - Cryptographic operations
- TwitterInfluenceSkill - Influence analysis

**Service Layer** (`src/talos/services/`): Abstract and concrete implementations for external integrations:
- GitHub service for repository management
- Twitter service for social media interaction
- Proposal service for governance workflows
- Yield management for DeFi operations

**Tool Management** (`src/talos/tools/`): Extensible tool system with:
- SupervisedTool base class requiring hypervisor approval
- Platform-specific tools (Twitter, GitHub, DexScreener)
- Document loading and search capabilities
- Memory management tools

### Data Flow

1. User input → MainAgent → Router → appropriate Service/Skill
2. Actions requiring approval → Hypervisor → approval/denial
3. Context building → DatasetManager → relevant document retrieval
4. Tool execution → ToolManager → supervised execution

## Code Style Guidelines

- Use `from __future__ import annotations` for forward references
- Prefer `list` and `dict` over `List` and `Dict` in type hints
- Use `model_post_init` for Pydantic model initialization logic
- Set `arbitrary_types_allowed=True` in ConfigDict for LangChain integration
- Default LLM model is `gpt-4o`
- Line length limit is 120 characters (configured in ruff)
- All function signatures require type hints

## Environment Variables

Required for full functionality:
- `OPENAI_API_KEY` - OpenAI API access
- `GITHUB_TOKEN` - GitHub API access  
- `PINATA_API_KEY` / `PINATA_SECRET_API_KEY` - IPFS storage
- Additional service-specific keys as needed
- Always run scripts/run_checks.sh after performing a large code change.
- ⏺ Code commenting principle: Only include comments that explain why something is done or provide context that isn't obvious from the code itself - avoid comments that simply restate what the code is doing, as these add noise without value.