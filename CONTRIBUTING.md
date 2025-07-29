# Contributing

Thank you for your interest in contributing to Talos! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/talos-agent/talos.git
   cd talos
   ```

2. **Set up the development environment**:
   ```bash
   uv venv
   source .venv/bin/activate
   ./scripts/install_deps.sh
   ```

3. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export PINATA_API_KEY="your-pinata-api-key"
   export PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
   # Optional for full functionality
   export GITHUB_API_TOKEN="your-github-token"
   export TWITTER_BEARER_TOKEN="your-twitter-bearer-token"
   export ARBISCAN_API_KEY="your-arbiscan-api-key"
   ```

## Code Quality Checks

Before submitting a pull request, ensure your code passes all checks:

### Linting and Formatting
```bash
uv run ruff check .
uv run ruff format .
```

### Type Checking
```bash
uv run mypy src
```

### Testing
```bash
uv run pytest
```

### Run All Checks
```bash
./scripts/run_checks.sh
```

## Code Style Guidelines

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use modern Python type hints (`list` and `dict` instead of `List` and `Dict`)
- Never use quotes around type hints
- Use type hints for all function signatures
- Write clear and concise docstrings for modules, classes, and functions
- Keep lines under 88 characters long
- Use `model_post_init` for Pydantic `BaseModel` post-initialization logic
- Organize imports: standard library, third-party, first-party
- Use `ConfigDict` for Pydantic model configuration

## Documentation Standards

- Update documentation when adding new features
- Include usage examples in CLI documentation
- Ensure README files are accurate and up-to-date
- Add docstrings to all public functions and classes
- Update environment variable documentation when adding new requirements

## Testing Guidelines

- Write tests for all new functionality
- Ensure existing tests continue to pass
- Include both unit tests and integration tests where appropriate
- Test error handling and edge cases
- Mock external API calls in tests

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Run all checks** to ensure code quality

4. **Commit your changes** with clear, descriptive commit messages

5. **Push your branch** and create a pull request

6. **Ensure CI passes** and address any feedback

## Commit Message Guidelines

- Use clear, descriptive commit messages
- Start with a verb in the imperative mood
- Keep the first line under 50 characters
- Include additional details in the body if needed

Examples:
```
Add memory search functionality to CLI

Implement semantic search for agent memories with user filtering
and configurable result limits. Includes both database and file
backend support.
```

## Issue Reporting

When reporting issues:
- Use the issue templates when available
- Provide clear reproduction steps
- Include relevant environment information
- Add logs or error messages when applicable

## Feature Requests

For feature requests:
- Clearly describe the proposed functionality
- Explain the use case and benefits
- Consider implementation complexity
- Discuss potential alternatives

## Getting Help

- Check existing documentation first
- Search existing issues and discussions
- Join our community channels for questions
- Tag maintainers for urgent issues

## License

By contributing to Talos, you agree that your contributions will be licensed under the MIT License.
