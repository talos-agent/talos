# Agent System

The agent system in Talos provides the foundation for AI-driven protocol management through a hierarchical architecture of specialized agents.

## Agent Hierarchy

### MainAgent

The `MainAgent` serves as the top-level orchestrator that integrates all system components:

```python
class MainAgent:
    def __init__(self):
        self.skills = []
        self.services = []
        self.hypervisor = Hypervisor()
        self.tool_manager = ToolManager()
        self.memory = Memory()
```

**Key Responsibilities:**
- **Query Routing** - Directs user queries to appropriate skills/services
- **Action Supervision** - Ensures all actions pass through hypervisor approval
- **Tool Coordination** - Manages available tools and their registration
- **Memory Management** - Maintains persistent conversation history
- **Skill Integration** - Orchestrates multiple skills for complex tasks

**Workflow:**
1. Receives user input
2. Routes query directly to appropriate skill/service
3. Executes actions through SupervisedTool wrappers
4. Stores results in Memory for future reference
5. Returns structured response to user

### Base Agent

The `Agent` class provides core functionality inherited by all specialized agents:

**Core Features:**
- **LLM Interaction** - Standardized interface to language models (default: GPT-4o)
- **Conversation History** - Maintains context across interactions using message history
- **Memory Integration** - Semantic search and retrieval of past conversations
- **Prompt Management** - Template-based prompt system with dynamic loading

**Implementation Details:**
```python
class Agent:
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.history = []
        self.memory = Memory()
        self.prompt_manager = PromptManager()
```

## Specialized Agents

### GitHub PR Review Agent

Specialized agent for automated code review:

**Capabilities:**
- **Code Analysis** - Reviews pull requests for quality and security
- **Security Scoring** - Assigns security scores (0-100) based on code analysis
- **Quality Assessment** - Evaluates code quality and adherence to standards
- **Automated Feedback** - Generates detailed review comments
- **Approval Workflow** - Can automatically approve PRs meeting criteria

**Integration:**
- Uses `GithubService` for repository operations
- Leverages `GithubTools` for API interactions
- Supervised through hypervisor for all actions

### Sentiment Analysis Agents

Specialized agents for social media and community sentiment:

**Twitter Sentiment Agent:**
- Analyzes tweet sentiment for specific queries
- Tracks trending topics and community discussions
- Evaluates account influence and credibility
- Generates sentiment reports with scoring

**Community Monitoring Agent:**
- Monitors multiple social platforms
- Aggregates sentiment across channels
- Identifies emerging trends and concerns
- Provides actionable insights for protocol decisions

## Agent Communication

### Message System

Agents communicate through a standardized message system:

```python
class Message:
    content: str
    role: str  # "human", "assistant", "system"
    metadata: dict
    timestamp: datetime
```

**Message Types:**
- **HumanMessage** - User input and queries
- **AIMessage** - Agent responses and analysis
- **SystemMessage** - Internal system communications

### History Management

**Conversation Persistence:**
- All interactions stored in persistent memory
- Semantic search enables context retrieval
- Message history maintains conversation flow
- Metadata enables filtering and categorization

**Memory Integration:**
- Vector embeddings for semantic similarity
- FAISS backend for efficient search
- Batch operations for performance optimization
- Automatic memory consolidation

## Agent Lifecycle

### Initialization

1. **Configuration Loading** - Load agent-specific settings
2. **Tool Registration** - Register available tools with ToolManager
3. **Memory Initialization** - Load persistent memory and history
4. **Prompt Loading** - Load prompt templates from files
5. **Service Integration** - Connect to external services (GitHub, Twitter, etc.)

### Execution Cycle

1. **Input Processing** - Parse and validate user input
2. **Context Retrieval** - Search memory for relevant context
3. **Skill Selection** - Route query to appropriate skill/service
4. **Action Planning** - Generate execution plan for complex tasks
5. **Supervised Execution** - Execute actions through hypervisor approval
6. **Result Processing** - Format and store results
7. **Response Generation** - Generate user-facing response

### Shutdown

1. **Memory Persistence** - Save conversation history and memories
2. **Tool Cleanup** - Properly close external connections
3. **State Serialization** - Save agent state for future sessions

## Agent Configuration

### Model Selection

Agents can be configured with different LLM models:

```python
# Default configuration
agent = Agent(model="gpt-4o")

# Custom model for specific tasks
code_review_agent = Agent(model="gpt-4o-code")
```

### Prompt Customization

Agents use template-based prompts that can be customized:

```json
{
  "system_prompt": "You are Talos, an AI protocol owner...",
  "task_prompts": {
    "proposal_evaluation": "Analyze the following proposal...",
    "sentiment_analysis": "Evaluate the sentiment of..."
  }
}
```

### Memory Configuration

Memory system can be tuned for different use cases:

```python
memory = Memory(
    batch_size=10,      # Batch writes for performance
    auto_save=True,     # Automatic persistence
    max_memories=1000   # Memory limit
)
```

## Best Practices

### Agent Design

- **Single Responsibility** - Each agent should have a clear, focused purpose
- **Stateless Operations** - Minimize agent state for reliability
- **Error Handling** - Robust error handling and recovery
- **Logging** - Comprehensive logging for debugging and monitoring

### Performance Optimization

- **Batch Operations** - Use batch processing for memory operations
- **Caching** - Cache frequently accessed data (prompts, configurations)
- **Lazy Loading** - Load resources only when needed
- **Connection Pooling** - Reuse connections to external services

### Security Considerations

- **Input Validation** - Validate all user inputs
- **Supervised Execution** - All actions must pass hypervisor approval
- **Audit Trails** - Maintain logs of all agent actions
- **Access Control** - Implement proper permissions for external services

This agent system provides the foundation for Talos's autonomous protocol management capabilities while maintaining security and reliability through supervised execution.
