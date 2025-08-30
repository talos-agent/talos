# Integration Tests

This directory contains comprehensive integration tests for the Talos agent that verify end-to-end functionality.

## Running Integration Tests

### Run all integration tests:
```bash
uv run pytest integration_tests/ -v
```

### Run specific test files:
```bash
uv run pytest integration_tests/test_memory_integration.py -v
uv run pytest integration_tests/test_memory_tool_availability.py -v
uv run pytest integration_tests/test_cli_memory.py -v
uv run pytest integration_tests/test_memory_prompt_fix.py -v
```

## Test Coverage

### Memory Functionality Tests
- **test_memory_integration.py**: Core memory tool registration and storage/retrieval
- **test_memory_tool_availability.py**: Memory tool availability and binding verification
- **test_cli_memory.py**: CLI-based memory functionality testing
- **test_memory_prompt_fix.py**: Prompt engineering verification for automatic memory usage

## Configuration

These tests are excluded from the default pytest run and GitHub Actions CI to keep the main test suite fast and focused. They can be run manually when needed for comprehensive verification.

## Test Requirements

- OpenAI API key (for LLM model testing)
- Full Talos environment setup
- May create temporary files and directories during execution
