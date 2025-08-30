# Testing Guide

This document provides comprehensive guidance on testing practices for the Talos project, including unit tests, integration tests, and end-to-end testing strategies.

## Testing Philosophy

Talos follows a comprehensive testing approach that ensures:
- **Reliability** - All core functionality is thoroughly tested
- **Security** - Security-critical components have extensive test coverage
- **Performance** - Performance characteristics are validated through testing
- **Maintainability** - Tests serve as documentation and prevent regressions

## Test Structure

### Directory Organization

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── core/
│   │   ├── test_agent.py
│   │   ├── test_memory.py
│   │   └── test_main_agent.py
│   ├── skills/
│   │   ├── test_proposals.py
│   │   ├── test_sentiment.py
│   │   └── test_twitter_sentiment.py
│   ├── services/
│   │   ├── test_yield_manager.py
│   │   └── test_github.py
│   ├── tools/
│   │   ├── test_twitter.py
│   │   └── test_github_tools.py
│   └── hypervisor/
│       ├── test_hypervisor.py
│       └── test_supervisor.py
├── integration/             # Integration tests
│   ├── test_agent_workflow.py
│   ├── test_github_integration.py
│   └── test_twitter_integration.py
├── e2e/                     # End-to-end tests
│   ├── test_proposal_evaluation.py
│   ├── test_sentiment_analysis.py
│   └── test_cli_workflows.py
├── performance/             # Performance tests
│   ├── test_memory_performance.py
│   └── test_api_performance.py
├── fixtures/                # Test fixtures and data
│   ├── sample_proposals.json
│   ├── mock_twitter_data.json
│   └── test_configs.yaml
└── conftest.py             # Pytest configuration and shared fixtures
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/core/test_agent.py

# Run tests matching pattern
uv run pytest -k "test_sentiment"

# Run tests with verbose output
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src --cov-report=html
```

### Test Categories

```bash
# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/

# Run only end-to-end tests
uv run pytest tests/e2e/

# Run performance tests
uv run pytest tests/performance/
```

### Continuous Testing

```bash
# Watch for changes and re-run tests
uv run pytest-watch

# Run tests in parallel
uv run pytest -n auto
```

## Unit Testing

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_agent_processes_query_successfully():
    # Arrange - Set up test data and dependencies
    agent = Agent(name="test_agent", model="gpt-5")
    query = "What is the current market sentiment?"
    expected_response_type = QueryResponse
    
    # Act - Execute the functionality being tested
    result = agent.process_query(query)
    
    # Assert - Verify the results
    assert result is not None
    assert isinstance(result, expected_response_type)
    assert len(result.answers) > 0
    assert result.answers[0].strip() != ""
```

### Mocking External Dependencies

Use mocks for external services and APIs:

```python
import pytest
from unittest.mock import Mock, patch, MagicMock
from talos.core.agent import Agent
from talos.tools.twitter_client import TwitterClient

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    client = Mock()
    client.chat.completions.create.return_value = Mock(
        choices=[Mock(message=Mock(content="Test response from AI"))]
    )
    return client

@pytest.fixture
def mock_twitter_client():
    """Mock Twitter client for testing."""
    client = Mock(spec=TwitterClient)
    client.search_tweets.return_value = [
        {"text": "Positive tweet about DeFi", "user": {"followers_count": 1000}},
        {"text": "Negative tweet about protocols", "user": {"followers_count": 500}}
    ]
    return client

def test_sentiment_analysis_with_mocked_twitter(mock_twitter_client):
    """Test sentiment analysis with mocked Twitter data."""
    with patch('talos.skills.twitter_sentiment.TwitterClient', return_value=mock_twitter_client):
        skill = TwitterSentimentSkill()
        result = skill.run(query="DeFi protocols", limit=10)
        
        assert result is not None
        assert isinstance(result, QueryResponse)
        mock_twitter_client.search_tweets.assert_called_once()
```

### Testing Error Conditions

Test error handling and edge cases:

```python
def test_agent_raises_error_for_empty_query():
    """Test that agent raises appropriate error for empty query."""
    agent = Agent(name="test_agent")
    
    with pytest.raises(ValidationError, match="Query cannot be empty"):
        agent.process_query("")

def test_agent_handles_api_timeout():
    """Test that agent handles API timeouts gracefully."""
    with patch('openai.OpenAI') as mock_openai:
        mock_openai.return_value.chat.completions.create.side_effect = TimeoutError("API timeout")
        
        agent = Agent(name="test_agent")
        
        with pytest.raises(APIError, match="API timeout"):
            agent.process_query("test query")
```

## Integration Testing

### Testing Component Interactions

Integration tests verify that components work together correctly:

```python
def test_agent_with_real_memory_integration():
    """Test agent with actual memory system integration."""
    # Create agent with real memory (not mocked)
    agent = Agent(name="integration_test_agent")
    
    # Add some memories
    agent.memory.add_memory("Previous conversation about DeFi", {"topic": "defi"})
    agent.memory.add_memory("Discussion about yield farming", {"topic": "yield"})
    
    # Query should use memory context
    result = agent.process_query("What did we discuss about DeFi before?")
    
    assert result is not None
    assert "DeFi" in str(result) or "defi" in str(result).lower()

def test_hypervisor_with_supervised_tools():
    """Test hypervisor integration with supervised tools."""
    hypervisor = Hypervisor()
    github_tool = GithubTool()
    supervised_tool = SupervisedTool(github_tool, hypervisor.supervisor)
    
    # Test that tool execution goes through approval
    with patch.object(hypervisor.supervisor, 'approve_action') as mock_approve:
        mock_approve.return_value = ApprovalResult(approved=True, reason="Test approval")
        
        result = supervised_tool.execute("get_prs", repo="test/repo")
        
        mock_approve.assert_called_once()
        assert result is not None
```

### Database Integration Tests

Test database operations with real database:

```python
@pytest.fixture
def test_database():
    """Create test database for integration tests."""
    # Set up test database
    db_path = "test_memory.db"
    memory = Memory(db_path=db_path)
    yield memory
    
    # Cleanup after test
    import os
    if os.path.exists(db_path):
        os.remove(db_path)

def test_memory_persistence_integration(test_database):
    """Test that memories persist across sessions."""
    memory = test_database
    
    # Add memory in first session
    memory.add_memory("Test memory for persistence", {"session": "first"})
    memory.flush()
    
    # Create new memory instance (simulating new session)
    new_memory = Memory(db_path=memory.db_path)
    
    # Search should find the persisted memory
    results = new_memory.search("Test memory", limit=1)
    assert len(results) == 1
    assert results[0].description == "Test memory for persistence"
```

## End-to-End Testing

### Complete Workflow Tests

Test entire user workflows from start to finish:

```python
def test_proposal_evaluation_workflow():
    """Test complete proposal evaluation workflow."""
    # Simulate user submitting a proposal
    proposal_text = """
    Proposal: Increase staking rewards from 5% to 8% APR
    
    Rationale: Current market conditions show competitors offering 
    higher yields. This increase will help maintain competitiveness 
    and attract more stakers to the protocol.
    """
    
    # Create main agent
    agent = MainAgent()
    
    # Process proposal evaluation request
    query = f"Please evaluate this governance proposal: {proposal_text}"
    result = agent.run(query)
    
    # Verify comprehensive evaluation
    assert result is not None
    assert isinstance(result, QueryResponse)
    assert len(result.answers) > 0
    
    response_text = str(result)
    assert "risk" in response_text.lower()
    assert "recommendation" in response_text.lower()
    assert any(word in response_text.lower() for word in ["approve", "reject", "modify"])

def test_cli_interactive_workflow():
    """Test CLI interactive mode workflow."""
    from talos.cli.main import interactive_mode
    from unittest.mock import patch
    import io
    import sys
    
    # Mock user input
    user_inputs = [
        "What are your capabilities?",
        "Analyze sentiment for 'DeFi protocols'",
        "exit"
    ]
    
    with patch('builtins.input', side_effect=user_inputs):
        # Capture output
        captured_output = io.StringIO()
        with patch('sys.stdout', captured_output):
            interactive_mode()
    
    output = captured_output.getvalue()
    assert "capabilities" in output.lower()
    assert len(output) > 100  # Should have substantial output
```

### API Integration Tests

Test external API integrations:

```python
@pytest.mark.integration
def test_twitter_api_integration():
    """Test actual Twitter API integration (requires API keys)."""
    import os
    
    # Skip if no API keys available
    if not os.getenv('TWITTER_BEARER_TOKEN'):
        pytest.skip("Twitter API keys not available")
    
    from talos.tools.twitter import TwitterTools
    
    twitter_tools = TwitterTools()
    
    # Test actual API call with a safe query
    result = twitter_tools.search_tweets("python programming", limit=5)
    
    assert isinstance(result, list)
    assert len(result) <= 5
    assert all('text' in tweet for tweet in result)

@pytest.mark.integration
def test_github_api_integration():
    """Test actual GitHub API integration (requires API token)."""
    import os
    
    if not os.getenv('GITHUB_API_TOKEN'):
        pytest.skip("GitHub API token not available")
    
    from talos.tools.github import GithubTools
    
    github_tools = GithubTools()
    
    # Test with a known public repository
    prs = github_tools.get_all_pull_requests("octocat", "Hello-World", state="all")
    
    assert isinstance(prs, list)
    assert all('number' in pr for pr in prs)
```

## Performance Testing

### Load Testing

Test system performance under load:

```python
import time
import concurrent.futures
from talos.core.memory import Memory

def test_memory_concurrent_access():
    """Test memory system under concurrent access."""
    memory = Memory(batch_size=10)
    
    def add_memories(thread_id: int, count: int):
        """Add memories from a specific thread."""
        for i in range(count):
            memory.add_memory(f"Memory {i} from thread {thread_id}", {"thread": thread_id})
    
    # Run concurrent memory additions
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(add_memories, i, 20) for i in range(5)]
        concurrent.futures.wait(futures)
    
    memory.flush()
    
    # Verify all memories were added
    all_memories = memory.search("Memory", limit=1000)
    assert len(all_memories) == 100  # 5 threads * 20 memories each

def test_agent_response_time():
    """Test that agent responses are within acceptable time limits."""
    agent = Agent(name="performance_test_agent")
    
    queries = [
        "What is DeFi?",
        "Explain yield farming",
        "How does staking work?",
        "What are governance tokens?",
        "Describe liquidity pools"
    ]
    
    response_times = []
    
    for query in queries:
        start_time = time.time()
        result = agent.process_query(query)
        end_time = time.time()
        
        response_time = end_time - start_time
        response_times.append(response_time)
        
        # Each response should be under 30 seconds
        assert response_time < 30.0
        assert result is not None
    
    # Average response time should be reasonable
    avg_response_time = sum(response_times) / len(response_times)
    assert avg_response_time < 15.0
```

### Memory Usage Testing

Test memory consumption patterns:

```python
import psutil
import os

def test_memory_usage_scaling():
    """Test that memory usage scales reasonably with data size."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    memory = Memory(batch_size=50)
    
    # Add a large number of memories
    for i in range(1000):
        memory.add_memory(f"Large memory entry {i} with substantial content " * 10)
    
    memory.flush()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Memory increase should be reasonable (less than 200MB for 1000 entries)
    assert memory_increase < 200 * 1024 * 1024
    
    # Test memory cleanup
    del memory
    
    # Memory should be released (allow some tolerance)
    cleanup_memory = process.memory_info().rss
    assert cleanup_memory < final_memory * 1.1
```

## Test Configuration

### Pytest Configuration

Create `conftest.py` with shared fixtures:

```python
import pytest
import os
import tempfile
from unittest.mock import Mock
from talos.core.agent import Agent
from talos.core.memory import Memory

@pytest.fixture(scope="session")
def test_config():
    """Test configuration for all tests."""
    return {
        "model": "gpt-5",
        "test_mode": True,
        "api_timeout": 30
    }

@pytest.fixture
def temp_directory():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def mock_api_keys(monkeypatch):
    """Mock API keys for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("GITHUB_API_TOKEN", "test-github-token")
    monkeypatch.setenv("TWITTER_BEARER_TOKEN", "test-twitter-token")

@pytest.fixture
def test_agent(mock_api_keys):
    """Create test agent with mocked dependencies."""
    return Agent(name="test_agent", model="gpt-5")

@pytest.fixture
def test_memory(temp_directory):
    """Create test memory instance."""
    memory_path = os.path.join(temp_directory, "test_memory")
    return Memory(memory_path=memory_path, batch_size=5)
```

### Test Markers

Use pytest markers to categorize tests:

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "e2e: End-to-end tests",
    "performance: Performance tests",
    "slow: Slow running tests",
    "api: Tests requiring API access"
]
```

Run specific test categories:

```bash
# Run only unit tests
uv run pytest -m unit

# Run integration and e2e tests
uv run pytest -m "integration or e2e"

# Skip slow tests
uv run pytest -m "not slow"

# Run only API tests (when keys are available)
uv run pytest -m api
```

## Continuous Integration

### GitHub Actions Configuration

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh
    
    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip install -e .
        uv pip install pytest pytest-cov pytest-mock
    
    - name: Run unit tests
      run: |
        source .venv/bin/activate
        uv run pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: |
        source .venv/bin/activate
        uv run pytest tests/integration/ -v
      env:
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        GITHUB_API_TOKEN: ${{ secrets.GITHUB_API_TOKEN }}
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

### Test Writing Guidelines

1. **Test Names**: Use descriptive names that explain the scenario
2. **Test Independence**: Each test should be independent and not rely on others
3. **Test Data**: Use realistic test data that represents actual usage
4. **Assertions**: Make specific assertions about expected behavior
5. **Error Testing**: Test both success and failure scenarios

### Mocking Guidelines

1. **Mock External Dependencies**: Always mock external APIs and services
2. **Mock at the Right Level**: Mock at the boundary of your system
3. **Verify Interactions**: Assert that mocked methods are called correctly
4. **Use Realistic Data**: Mock responses should match real API responses

### Performance Testing

1. **Set Realistic Limits**: Base performance expectations on actual requirements
2. **Test Under Load**: Test with realistic data volumes and concurrent users
3. **Monitor Resources**: Track memory, CPU, and network usage
4. **Establish Baselines**: Create performance baselines to detect regressions

### Test Maintenance

1. **Keep Tests Updated**: Update tests when functionality changes
2. **Remove Obsolete Tests**: Delete tests for removed functionality
3. **Refactor Test Code**: Apply same quality standards to test code
4. **Document Complex Tests**: Add comments for complex test scenarios

This comprehensive testing approach ensures that Talos remains reliable, performant, and maintainable as it evolves.
