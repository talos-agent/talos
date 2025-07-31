# Core API Reference

This document provides detailed API reference for the core components of the Talos system.

## Agent Classes

### Agent

The base agent class that provides core functionality for all AI agents in the system.

```python
class Agent:
    def __init__(
        self, 
        name: str, 
        model: str = "gpt-4o",
        memory: Optional[Memory] = None
    ):
        """Initialize an agent with specified configuration.
        
        Args:
            name: Unique identifier for the agent
            model: LLM model to use (default: "gpt-4o")
            memory: Optional memory instance for conversation history
        """
```

#### Methods

##### `process_query(query: str) -> QueryResponse`

Process a user query and return a structured response.

**Parameters:**
- `query` (str): The user's query or request

**Returns:**
- `QueryResponse`: Structured response containing answers and metadata

**Raises:**
- `ValidationError`: If query is empty or invalid
- `APIError`: If LLM service is unavailable

**Example:**
```python
agent = Agent(name="my_agent")
response = agent.process_query("What is the current market sentiment?")
print(response.answers[0])
```

##### `add_memory(description: str, metadata: Optional[dict] = None) -> None`

Add a memory to the agent's persistent memory system.

**Parameters:**
- `description` (str): Description of the memory to store
- `metadata` (Optional[dict]): Additional metadata for the memory

**Example:**
```python
agent.add_memory(
    "User prefers conservative investment strategies",
    {"category": "preference", "importance": "high"}
)
```

##### `search_memory(query: str, limit: int = 10) -> List[Memory]`

Search the agent's memory for relevant information.

**Parameters:**
- `query` (str): Search query
- `limit` (int): Maximum number of results to return

**Returns:**
- `List[Memory]`: List of relevant memories

### MainAgent

The primary agent that orchestrates all system components and handles user interactions.

```python
class MainAgent(Agent):
    def __init__(self):
        """Initialize the main agent with all system components."""
```

#### Methods

##### `run(query: str, history: Optional[List[Message]] = None) -> AIMessage`

Execute a query through the complete system pipeline.

**Parameters:**
- `query` (str): User query to process
- `history` (Optional[List[Message]]): Conversation history

**Returns:**
- `AIMessage`: AI response message

**Example:**
```python
main_agent = MainAgent()
response = main_agent.run("Analyze the latest governance proposal")
print(response.content)
```

## Memory System

### Memory

Persistent memory system with semantic search capabilities.

```python
class Memory:
    def __init__(
        self,
        agent_name: str,
        batch_size: int = 10,
        auto_save: bool = True
    ):
        """Initialize memory system.
        
        Args:
            agent_name: Name of the agent using this memory
            batch_size: Number of memories to batch before writing
            auto_save: Whether to automatically save on destruction
        """
```

#### Methods

##### `add_memory(description: str, metadata: Optional[dict] = None) -> None`

Add a new memory with optional metadata.

**Parameters:**
- `description` (str): Memory description
- `metadata` (Optional[dict]): Additional metadata

##### `search(query: str, limit: int = 10) -> List[MemoryItem]`

Search memories using semantic similarity.

**Parameters:**
- `query` (str): Search query
- `limit` (int): Maximum results to return

**Returns:**
- `List[MemoryItem]`: Relevant memories sorted by similarity

##### `flush() -> None`

Manually flush pending writes to persistent storage.

### MemoryItem

Individual memory item with metadata and embeddings.

```python
class MemoryItem(BaseModel):
    description: str
    metadata: dict
    timestamp: datetime
    embedding: Optional[List[float]] = None
```

## Skill and Service Management

Skills and services are now managed directly by the MainAgent without a separate Router component.

##### `register_skill(skill: Skill, keywords: List[str]) -> None`

Register a skill with associated keywords for routing.

**Parameters:**
- `skill` (Skill): Skill instance to register
- `keywords` (List[str]): Keywords that trigger this skill

##### `register_service(service: Service, keywords: List[str]) -> None`

Register a service with associated keywords for routing.

**Parameters:**
- `service` (Service): Service instance to register
- `keywords` (List[str]): Keywords that trigger this service

##### `route(query: str) -> Union[Skill, Service, None]`

Route a query to the most appropriate skill or service.

**Parameters:**
- `query` (str): User query to route

**Returns:**
- `Union[Skill, Service, None]`: Best matching handler or None

## Data Models

### QueryResponse

Structured response from agent queries.

```python
class QueryResponse(BaseModel):
    answers: List[str]
    metadata: dict = Field(default_factory=dict)
    confidence: Optional[float] = None
    sources: List[str] = Field(default_factory=list)
```

### Message

Base message class for conversation history.

```python
class Message(BaseModel):
    content: str
    role: str  # "human", "assistant", "system"
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: dict = Field(default_factory=dict)
```

### HumanMessage

Message from human users.

```python
class HumanMessage(Message):
    role: str = "human"
```

### AIMessage

Message from AI agents.

```python
class AIMessage(Message):
    role: str = "assistant"
```

### SystemMessage

System-generated messages.

```python
class SystemMessage(Message):
    role: str = "system"
```

## Configuration

### AgentConfig

Configuration for agent initialization.

```python
class AgentConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    model: str = "gpt-4o"
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1000, gt=0)
    memory_enabled: bool = True
    batch_size: int = Field(default=10, gt=0)
```

### MemoryConfig

Configuration for memory system.

```python
class MemoryConfig(BaseModel):
    batch_size: int = Field(default=10, gt=0)
    auto_save: bool = True
    max_memories: Optional[int] = None
    embedding_model: str = "text-embedding-ada-002"
```

## Error Classes

### TalosError

Base exception for all Talos-specific errors.

```python
class TalosError(Exception):
    """Base exception for all Talos errors."""
    pass
```

### ValidationError

Raised when input validation fails.

```python
class ValidationError(TalosError):
    """Raised when input validation fails."""
    pass
```

### APIError

Raised when external API calls fail.

```python
class APIError(TalosError):
    """Raised when external API calls fail."""
    
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code
```

### ConfigurationError

Raised when configuration is invalid.

```python
class ConfigurationError(TalosError):
    """Raised when configuration is invalid."""
    pass
```

## Usage Examples

### Basic Agent Usage

```python
from talos.core.agent import Agent
from talos.core.memory import Memory

# Create agent with custom memory
memory = Memory(agent_name="example_agent", batch_size=5)
agent = Agent(name="example_agent", memory=memory)

# Process queries
response = agent.process_query("What are the latest DeFi trends?")
print(f"Response: {response.answers[0]}")

# Add memories
agent.add_memory("User is interested in DeFi trends", {"topic": "defi"})

# Search memories
memories = agent.search_memory("DeFi", limit=5)
for memory in memories:
    print(f"Memory: {memory.description}")
```

### Main Agent Usage

```python
from talos.core.main_agent import MainAgent

# Create main agent (includes all system components)
main_agent = MainAgent()

# Process complex queries
response = main_agent.run("Analyze sentiment for 'yield farming' and recommend APR adjustments")
print(response.content)

# Interactive conversation
history = []
while True:
    user_input = input(">> ")
    if user_input.lower() == 'exit':
        break
    
    response = main_agent.run(user_input, history=history)
    print(response.content)
    
    # History is automatically managed by the agent
```

### Memory System Usage

```python
from talos.core.memory import Memory

# Create memory system
memory = Memory(agent_name="test_agent", batch_size=20)

# Add memories with metadata
memory.add_memory(
    "Protocol X increased APR to 12% due to market competition",
    {
        "protocol": "Protocol X",
        "action": "apr_increase",
        "value": 0.12,
        "reason": "competition"
    }
)

# Search for relevant memories
results = memory.search("APR increase competition", limit=10)
for result in results:
    print(f"Memory: {result.description}")
    print(f"Metadata: {result.metadata}")

# Manual flush if needed
memory.flush()
```

### MainAgent Skill Management

```python
from talos.core.main_agent import MainAgent
from talos.skills.proposals import ProposalsSkill
from talos.skills.twitter_sentiment import TwitterSentimentSkill

# Create main agent (skills are automatically registered)
agent = MainAgent(model=model, prompts_dir="prompts")

# Skills are managed directly by MainAgent
# Access skills through agent.skills list
for skill in agent.skills:
    print(f"Available skill: {skill.name}")

# Use agent to process queries
result = agent.run("Analyze this governance proposal")
print(result)
```

## Error Handling

All core API methods include comprehensive error handling. Always wrap API calls in try-catch blocks:

```python
from talos.core.agent import Agent
from talos.core.exceptions import ValidationError, APIError

agent = Agent(name="example")

try:
    response = agent.process_query("What is DeFi?")
    print(response.answers[0])
except ValidationError as e:
    print(f"Invalid input: {e}")
except APIError as e:
    print(f"API error: {e}")
    if e.status_code:
        print(f"Status code: {e.status_code}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

### Memory Management

- Use batch operations for multiple memory additions
- Call `flush()` manually for time-sensitive operations
- Monitor memory usage in long-running processes

### API Rate Limiting

- Implement backoff strategies for API calls
- Cache responses when appropriate
- Use connection pooling for external services

### Concurrency

- Core components are thread-safe for read operations
- Use locks for concurrent write operations
- Consider async patterns for I/O-bound operations

This API reference provides the foundation for building applications with the Talos core system. For specific integrations and advanced usage patterns, refer to the Skills and Services API documentation.
