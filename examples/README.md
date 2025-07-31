# Talos Examples

This directory contains example implementations and demonstrations of Talos functionality.

## LangGraph Interactive Example

### Overview

The `langgraph_interactive_example.py` demonstrates a complete multi-step DAG (Directed Acyclic Graph) implementation using LangGraph with the following features:

- **Multi-step processing pipeline** with 4 distinct stages
- **Conditional branching** that routes queries to specialized processors
- **Memory persistence** using LangGraph's MemorySaver
- **Interactive CLI** for testing different scenarios
- **State management** that flows through all nodes

### DAG Architecture

```
START → query_analyzer → router → [sentiment|proposal|general]_processor → output_formatter → END
```

#### Node Types:

1. **query_analyzer**: Analyzes incoming queries for intent and content
2. **router**: Determines which specialized processor to use based on keywords
3. **sentiment_processor**: Handles sentiment analysis and emotional content
4. **proposal_processor**: Processes governance and DAO-related queries  
5. **general_processor**: Handles general-purpose queries
6. **output_formatter**: Creates final structured responses

#### Branching Logic:

- **Sentiment path**: Triggered by keywords like "sentiment", "feeling", "twitter", "social"
- **Proposal path**: Triggered by keywords like "proposal", "governance", "vote", "dao"
- **General path**: Default path for all other queries

### Usage

#### Prerequisites

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

#### Running the Example

```bash
# From the talos root directory
cd ~/repos/talos
python examples/langgraph_interactive_example.py
```

#### Example Queries

The demo includes several pre-configured example queries that demonstrate different processing paths:

1. **Sentiment Analysis**: "What's the sentiment around the latest protocol update on Twitter?"
2. **Governance**: "I need help evaluating this governance proposal for the DAO"  
3. **General**: "Can you explain how blockchain consensus mechanisms work?"
4. **Emotional**: "The community seems really excited about the new features!"
5. **Risk Assessment**: "What are the risks of implementing this treasury management proposal?"

### Key Features Demonstrated

#### 1. Multi-Step DAG Execution
Each query goes through exactly 4 processing steps, demonstrating the sequential nature of the DAG while allowing for parallel processing paths.

#### 2. Conditional Branching
The router node analyzes query content and routes to appropriate specialized processors, showing how LangGraph handles conditional logic.

#### 3. State Management
The `AgentState` TypedDict flows through all nodes, accumulating results and maintaining context throughout the execution.

#### 4. Memory Persistence
Uses LangGraph's `MemorySaver` with thread-based conversation tracking, allowing for stateful interactions.

#### 5. Error Handling
Comprehensive error handling with graceful fallbacks and informative error messages.

### Technical Implementation

#### State Schema
```python
class AgentState(TypedDict):
    messages: List[BaseMessage]
    query: str
    query_type: str
    analysis_result: Dict[str, Any]
    processing_result: Dict[str, Any]
    final_output: str
    metadata: Dict[str, Any]
```

#### Graph Construction
```python
workflow = StateGraph(AgentState)
workflow.add_node("query_analyzer", self._analyze_query)
workflow.add_node("router", self._route_query)
# ... additional nodes

workflow.add_conditional_edges(
    "router",
    self._determine_next_node,
    {
        "sentiment": "sentiment_processor",
        "proposal": "proposal_processor", 
        "general": "general_processor"
    }
)
```

### Integration with Talos

This example is designed to be:
- **Standalone**: Can run independently without modifying core Talos functionality
- **Educational**: Clearly demonstrates LangGraph concepts and patterns
- **Extensible**: Easy to add new node types and routing logic
- **Compatible**: Uses the same patterns as the existing Talos DAG implementation

### Extending the Example

To add new processing paths:

1. Create a new processor function (e.g., `_process_crypto_query`)
2. Add the node to the workflow: `workflow.add_node("crypto_processor", self._process_crypto_query)`
3. Update the routing logic in `_route_query` and `_determine_next_node`
4. Add the new path to conditional edges
5. Connect the new processor to the output formatter

### Troubleshooting

**Common Issues:**

1. **Missing API Key**: Ensure `OPENAI_API_KEY` is set in your environment
2. **Import Errors**: Make sure you're running from the talos root directory
3. **Model Access**: The example uses `gpt-4o-mini` - ensure your API key has access

**Debug Mode:**
The example includes verbose logging that shows each step of the DAG execution, making it easy to understand the flow and debug issues.
