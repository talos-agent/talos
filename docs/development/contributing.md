# Contributing

Thank you for your interest in contributing to Talos! This guide will help you get started with contributing to the project.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended)
- Git
- Basic understanding of AI agents and DeFi protocols

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/talos.git
   cd talos
   ```

2. **Create a virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   ./scripts/install_deps.sh
   ```

4. **Set up environment variables**:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   export PINATA_API_KEY="your-pinata-api-key"
   export PINATA_SECRET_API_KEY="your-pinata-secret-api-key"
   ```

5. **Run tests to verify setup**:
   ```bash
   ./scripts/run_checks.sh
   ```

## Development Workflow

### Branch Management

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style guidelines

3. **Run pre-commit checks**:
   ```bash
   ./scripts/run_checks.sh
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

Follow conventional commit format:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add sentiment analysis for Twitter data
fix: resolve memory leak in agent initialization
docs: update API documentation for new endpoints
```

## Code Quality Standards

### Pre-commit Checks

Before committing any changes, ensure you run the following checks:

1. **Ruff** - Lint and format the code:
   ```bash
   uv run ruff check .
   uv run ruff format .
   ```

2. **Mypy** - Type checking:
   ```bash
   uv run mypy src
   ```

3. **Pytest** - Run all tests:
   ```bash
   uv run pytest
   ```

### Automated Checks

Run all checks at once:
```bash
./scripts/run_checks.sh
```

This script runs:
- Ruff linting and formatting
- Mypy type checking
- Pytest test suite

## Code Style Guidelines

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for all Python code
- Use modern Python type hints (`list` and `dict` instead of `List` and `Dict`)
- Never use quotes around type hints
- Use type hints for all function signatures
- Write clear and concise docstrings for all modules, classes, and functions
- Keep lines under 88 characters long

### Type Hints

```python
# Good
def process_data(items: list[str]) -> dict[str, int]:
    """Process a list of items and return counts."""
    return {item: len(item) for item in items}

# Bad
def process_data(items: "List[str]") -> "Dict[str, int]":
    return {item: len(item) for item in items}
```

### Pydantic Models

When creating Pydantic `BaseModel`s:
- Use `model_post_init` for post-initialization logic instead of overriding `__init__`
- Use `ConfigDict` for model-specific configuration

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    value: int
    
    def model_post_init(self, __context):
        # Post-initialization logic here
        pass
```

### Import Organization

Always put imports at the top of the file, organized into sections:

```python
# Standard library imports
import os
import sys
from datetime import datetime

# Third-party imports
import requests
from pydantic import BaseModel

# First-party imports
from talos.core.agent import Agent
from talos.utils.helpers import format_response
```

## Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test setup

```python
def test_agent_processes_query_successfully():
    # Arrange
    agent = Agent(model="gpt-5")
    query = "What is the current market sentiment?"
    
    # Act
    result = agent.process_query(query)
    
    # Assert
    assert result is not None
    assert isinstance(result, QueryResponse)
    assert len(result.answers) > 0
```

### Test Categories

- **Unit Tests** - Test individual functions and classes
- **Integration Tests** - Test component interactions
- **End-to-End Tests** - Test complete workflows
- **Performance Tests** - Test performance characteristics

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_agent.py

# Run with coverage
uv run pytest --cov=src

# Run tests matching pattern
uv run pytest -k "test_sentiment"
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def analyze_sentiment(text: str, model: str = "gpt-5") -> float:
    """Analyze sentiment of the given text.
    
    Args:
        text: The text to analyze for sentiment.
        model: The LLM model to use for analysis.
        
    Returns:
        A sentiment score between -1.0 (negative) and 1.0 (positive).
        
    Raises:
        ValueError: If text is empty or model is not supported.
        
    Example:
        >>> score = analyze_sentiment("I love this protocol!")
        >>> print(f"Sentiment: {score}")
        Sentiment: 0.8
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")
    
    # Implementation here
    return 0.0
```

### API Documentation

- Document all public APIs
- Include examples in docstrings
- Update documentation when changing APIs
- Use type hints consistently

## Architecture Guidelines

### Adding New Skills

When adding new skills to Talos:

1. **Inherit from base Skill class**:
   ```python
   from talos.skills.base import Skill
   
   class MyNewSkill(Skill):
       def run(self, **kwargs) -> QueryResponse:
           # Implementation
           pass
   ```

2. **Add to MainAgent setup**:
   ```python
   # Skills are automatically registered in MainAgent._setup_skills_and_services()
   # Add your skill to the skills list in that method
   ```

3. **Add comprehensive tests**
4. **Update documentation**

### Adding New Services

When adding new services:

1. **Inherit from base Service class**:
   ```python
   from talos.services.abstract.service import Service
   
   class MyNewService(Service):
       def process(self, request: ServiceRequest) -> ServiceResponse:
           # Implementation
           pass
   ```

2. **Follow single responsibility principle**
3. **Make services stateless when possible**
4. **Add proper error handling**

### Adding New Tools

When adding new tools:

1. **Inherit from BaseTool**
2. **Wrap with SupervisedTool for security**
3. **Add comprehensive error handling**
4. **Document all parameters and return values**

## Security Guidelines

### API Keys and Secrets

- Never commit API keys or secrets to the repository
- Use environment variables for sensitive configuration
- Add sensitive files to `.gitignore`
- Use the secrets management system for production

### Input Validation

- Validate all user inputs
- Sanitize data before processing
- Use type hints and Pydantic models for validation
- Handle edge cases gracefully

### Error Handling

- Don't expose sensitive information in error messages
- Log errors appropriately for debugging
- Provide helpful error messages to users
- Use proper exception handling

## Performance Guidelines

### Memory Management

- Use batch operations for memory-intensive tasks
- Implement proper cleanup in destructors
- Monitor memory usage in long-running processes
- Use generators for large datasets

### API Usage

- Implement proper rate limiting
- Use caching for frequently accessed data
- Batch API calls when possible
- Handle API errors gracefully

## Getting Help

### Resources

- **Documentation** - Check the full documentation for detailed guides
- **Issues** - Search existing issues before creating new ones
- **Discussions** - Use GitHub Discussions for questions and ideas
- **Code Review** - Request reviews from maintainers

### Communication

- Be respectful and constructive in all interactions
- Provide clear descriptions of issues and proposed changes
- Include relevant context and examples
- Follow up on feedback and suggestions

### Issue Reporting

When reporting bugs:

1. **Check existing issues** first
2. **Provide clear reproduction steps**
3. **Include relevant logs and error messages**
4. **Specify your environment** (OS, Python version, etc.)
5. **Use the issue template** if available

### Feature Requests

When requesting features:

1. **Describe the use case** clearly
2. **Explain the expected behavior**
3. **Consider the impact** on existing functionality
4. **Provide examples** if possible

## Release Process

### Version Management

- Follow semantic versioning (SemVer)
- Update version numbers in appropriate files
- Create release notes for significant changes
- Tag releases appropriately

### Deployment

- Ensure all tests pass before release
- Update documentation for new features
- Coordinate with maintainers for release timing
- Monitor for issues after release

Thank you for contributing to Talos! Your contributions help make decentralized protocol management more accessible and secure.
