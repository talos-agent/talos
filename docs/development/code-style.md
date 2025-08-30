# Code Style Guide

This document outlines the code style guidelines for the Talos project. Following these guidelines ensures consistency, readability, and maintainability across the codebase.

## Python Code Style

### PEP 8 Compliance

All Python code must follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines:

- Use 4 spaces for indentation (no tabs)
- Keep lines under 88 characters long
- Use lowercase with underscores for function and variable names
- Use CamelCase for class names
- Use UPPER_CASE for constants

### Type Hints

Use modern Python type hints consistently:

```python
# Good - Modern type hints
def process_items(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}

def get_user_data(user_id: int) -> dict[str, Any] | None:
    return database.get_user(user_id)

# Bad - Old-style type hints
from typing import List, Dict, Optional

def process_items(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

def get_user_data(user_id: int) -> Optional[Dict[str, Any]]:
    return database.get_user(user_id)
```

### Type Hint Guidelines

- **Never use quotes** around type hints unless absolutely necessary
- Use `from __future__ import annotations` if you need forward references
- Provide type hints for all function signatures
- Use `Any` sparingly and document why it's necessary

```python
# Good
from __future__ import annotations

def create_agent(config: AgentConfig) -> Agent:
    return Agent(config)

# Bad
def create_agent(config: "AgentConfig") -> "Agent":
    return Agent(config)
```

### Import Organization

Organize imports into three sections with blank lines between them:

```python
# Standard library imports
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Third-party imports
import requests
from pydantic import BaseModel, Field
from openai import OpenAI

# First-party imports
from talos.core.agent import Agent
from talos.core.memory import Memory
from talos.utils.helpers import format_response
```

### Docstrings

Use Google-style docstrings for all modules, classes, and functions:

```python
def analyze_sentiment(
    text: str, 
    model: str = "gpt-5",
    confidence_threshold: float = 0.7
) -> SentimentResult:
    """Analyze sentiment of the given text using an LLM.
    
    This function processes text through a language model to determine
    sentiment polarity and confidence scores.
    
    Args:
        text: The text to analyze for sentiment. Must not be empty.
        model: The LLM model to use for analysis. Defaults to "gpt-5".
        confidence_threshold: Minimum confidence score to return results.
            Must be between 0.0 and 1.0.
            
    Returns:
        SentimentResult containing polarity score (-1.0 to 1.0) and 
        confidence score (0.0 to 1.0).
        
    Raises:
        ValueError: If text is empty or confidence_threshold is invalid.
        APIError: If the LLM service is unavailable.
        
    Example:
        >>> result = analyze_sentiment("I love this protocol!")
        >>> print(f"Sentiment: {result.polarity}, Confidence: {result.confidence}")
        Sentiment: 0.8, Confidence: 0.95
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")
    
    if not 0.0 <= confidence_threshold <= 1.0:
        raise ValueError("Confidence threshold must be between 0.0 and 1.0")
    
    # Implementation here
    return SentimentResult(polarity=0.8, confidence=0.95)
```

## Pydantic Models

### Model Configuration

Use `ConfigDict` for model-specific configuration:

```python
from pydantic import BaseModel, ConfigDict, Field

class AgentConfig(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    model_name: str = Field(default="gpt-5", description="LLM model to use")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
```

### Post-Initialization Logic

Use `model_post_init` instead of overriding `__init__`:

```python
class Agent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    model: str = "gpt-5"
    memory: Memory | None = None
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize memory after model creation."""
        if self.memory is None:
            self.memory = Memory(agent_name=self.name)
```

### Field Validation

Use Pydantic validators for complex validation:

```python
from pydantic import BaseModel, field_validator, model_validator

class TwitterQuery(BaseModel):
    query: str
    limit: int = 100
    days_back: int = 7
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v) > 500:
            raise ValueError('Query too long (max 500 characters)')
        return v.strip()
    
    @field_validator('limit')
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if not 1 <= v <= 1000:
            raise ValueError('Limit must be between 1 and 1000')
        return v
    
    @model_validator(mode='after')
    def validate_model(self) -> 'TwitterQuery':
        if self.days_back > 30 and self.limit > 100:
            raise ValueError('Cannot use high limit with long time range')
        return self
```

## Error Handling

### Exception Hierarchy

Create custom exceptions for different error types:

```python
class TalosError(Exception):
    """Base exception for all Talos errors."""
    pass

class ConfigurationError(TalosError):
    """Raised when configuration is invalid."""
    pass

class APIError(TalosError):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code

class ValidationError(TalosError):
    """Raised when input validation fails."""
    pass
```

### Error Handling Patterns

Use specific exception handling and provide helpful error messages:

```python
def fetch_twitter_data(query: str) -> list[dict[str, Any]]:
    """Fetch Twitter data with proper error handling."""
    try:
        response = twitter_client.search(query)
        return response.data
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            raise APIError(
                "Twitter API rate limit exceeded. Please try again later.",
                status_code=429
            ) from e
        elif e.response.status_code == 401:
            raise APIError(
                "Twitter API authentication failed. Check your bearer token.",
                status_code=401
            ) from e
        else:
            raise APIError(f"Twitter API error: {e}", status_code=e.response.status_code) from e
    except requests.RequestException as e:
        raise APIError(f"Network error while fetching Twitter data: {e}") from e
    except Exception as e:
        raise TalosError(f"Unexpected error fetching Twitter data: {e}") from e
```

## Logging

### Logger Configuration

Use structured logging with appropriate levels:

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)

class Agent:
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def process_query(self, query: str) -> QueryResponse:
        self.logger.info("Processing query", extra={
            "agent_name": self.name,
            "query_length": len(query),
            "query_hash": hash(query)
        })
        
        try:
            result = self._execute_query(query)
            self.logger.info("Query processed successfully", extra={
                "agent_name": self.name,
                "response_length": len(str(result))
            })
            return result
        except Exception as e:
            self.logger.error("Query processing failed", extra={
                "agent_name": self.name,
                "error": str(e),
                "error_type": type(e).__name__
            }, exc_info=True)
            raise
```

### Log Levels

Use appropriate log levels:

- **DEBUG** - Detailed information for debugging
- **INFO** - General information about program execution
- **WARNING** - Something unexpected happened but the program continues
- **ERROR** - A serious problem occurred
- **CRITICAL** - A very serious error occurred

## Testing Style

### Test Organization

Organize tests to mirror the source code structure:

```
tests/
├── unit/
│   ├── core/
│   │   ├── test_agent.py
│   │   └── test_memory.py
│   ├── skills/
│   │   └── test_sentiment.py
│   └── services/
│       └── test_yield_manager.py
├── integration/
│   ├── test_github_integration.py
│   └── test_twitter_integration.py
└── e2e/
    └── test_full_workflow.py
```

### Test Naming

Use descriptive test names that explain the scenario:

```python
def test_agent_processes_simple_query_successfully():
    """Test that agent can process a simple query and return valid response."""
    pass

def test_agent_raises_error_when_query_is_empty():
    """Test that agent raises ValidationError when given empty query."""
    pass

def test_sentiment_analysis_returns_positive_score_for_positive_text():
    """Test that sentiment analysis correctly identifies positive sentiment."""
    pass
```

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_memory_stores_and_retrieves_data():
    # Arrange
    memory = Memory(agent_name="test_agent")
    test_data = "This is a test memory"
    metadata = {"type": "test", "importance": "high"}
    
    # Act
    memory.add_memory(test_data, metadata)
    results = memory.search("test memory", limit=1)
    
    # Assert
    assert len(results) == 1
    assert results[0].description == test_data
    assert results[0].metadata == metadata
```

### Fixtures and Mocking

Use fixtures for common test setup:

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response"))]
    )
    return client

@pytest.fixture
def test_agent(mock_openai_client):
    """Create test agent with mocked dependencies."""
    with patch('talos.core.agent.OpenAI', return_value=mock_openai_client):
        return Agent(name="test_agent", model="gpt-5")

def test_agent_generates_response(test_agent):
    """Test that agent generates appropriate response."""
    response = test_agent.process_query("What is the weather?")
    assert response is not None
    assert isinstance(response, QueryResponse)
```

## Performance Guidelines

### Memory Management

Write memory-efficient code:

```python
# Good - Use generators for large datasets
def process_large_dataset(data_source: str) -> Iterator[ProcessedItem]:
    """Process large dataset efficiently using generators."""
    with open(data_source) as file:
        for line in file:
            yield process_line(line)

# Good - Use context managers for resource cleanup
def analyze_file(file_path: str) -> AnalysisResult:
    """Analyze file with proper resource management."""
    with open(file_path) as file:
        content = file.read()
        return analyze_content(content)

# Bad - Loading entire dataset into memory
def process_large_dataset_bad(data_source: str) -> list[ProcessedItem]:
    with open(data_source) as file:
        all_lines = file.readlines()  # Loads entire file into memory
        return [process_line(line) for line in all_lines]
```

### Async Programming

Use async/await for I/O-bound operations:

```python
import asyncio
import aiohttp
from typing import AsyncIterator

async def fetch_multiple_urls(urls: list[str]) -> list[dict[str, Any]]:
    """Fetch multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if not isinstance(r, Exception)]

async def fetch_url(session: aiohttp.ClientSession, url: str) -> dict[str, Any]:
    """Fetch single URL with error handling."""
    try:
        async with session.get(url) as response:
            return await response.json()
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        raise
```

## Security Guidelines

### Input Validation

Always validate and sanitize inputs:

```python
def process_user_query(query: str, user_id: int) -> QueryResponse:
    """Process user query with proper validation."""
    # Validate input parameters
    if not isinstance(query, str):
        raise ValidationError("Query must be a string")
    
    if not query.strip():
        raise ValidationError("Query cannot be empty")
    
    if len(query) > 10000:
        raise ValidationError("Query too long (max 10000 characters)")
    
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValidationError("Invalid user ID")
    
    # Sanitize query to prevent injection attacks
    sanitized_query = sanitize_query(query)
    
    # Process the sanitized query
    return execute_query(sanitized_query, user_id)
```

### Secret Management

Never hardcode secrets or API keys:

```python
import os
from typing import Optional

def get_api_key(service: str) -> str:
    """Get API key from environment variables."""
    key_name = f"{service.upper()}_API_KEY"
    api_key = os.getenv(key_name)
    
    if not api_key:
        raise ConfigurationError(f"Missing required environment variable: {key_name}")
    
    return api_key

# Good - Use environment variables
openai_key = get_api_key("openai")

# Bad - Hardcoded secrets
# openai_key = "sk-1234567890abcdef"  # Never do this!
```

## Documentation Style

### Code Comments

Write clear, helpful comments:

```python
def calculate_optimal_apr(
    market_data: MarketData,
    sentiment_score: float,
    current_apr: float
) -> float:
    """Calculate optimal APR based on market conditions and sentiment."""
    
    # Base APR adjustment based on market volatility
    # Higher volatility requires higher APR to attract users
    volatility_adjustment = market_data.volatility * 0.1
    
    # Sentiment adjustment: positive sentiment allows lower APR
    # Negative sentiment requires higher APR to maintain attractiveness
    sentiment_adjustment = (0.5 - sentiment_score) * 0.05
    
    # Calculate new APR with bounds checking
    new_apr = current_apr + volatility_adjustment + sentiment_adjustment
    
    # Ensure APR stays within reasonable bounds (1% to 20%)
    return max(0.01, min(0.20, new_apr))
```

### README and Documentation

Keep documentation up to date and comprehensive:

- Explain the purpose and scope of each module
- Provide usage examples
- Document configuration options
- Include troubleshooting guides
- Maintain API documentation

Following these code style guidelines ensures that the Talos codebase remains clean, maintainable, and accessible to all contributors.
