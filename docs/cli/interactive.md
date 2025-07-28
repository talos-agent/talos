# Interactive Mode

Interactive mode provides a conversational interface for working with Talos, allowing for natural language queries and continuous dialogue.

## Starting Interactive Mode

Launch interactive mode by running Talos without arguments:

```bash
uv run talos
```

You'll see a prompt where you can start conversing:

```
Talos AI Agent - Interactive Mode
Type 'exit' to quit

>> 
```

## Basic Usage

### Simple Queries

Ask questions in natural language:

```
>> What are your main capabilities?
>> How is the current market sentiment?
>> What governance proposals need review?
```

### Complex Requests

Request detailed analysis and recommendations:

```
>> Analyze the sentiment around "yield farming" on Twitter and recommend APR adjustments
>> Review the latest GitHub PRs and identify any security concerns
>> Evaluate the community response to our latest protocol update
```

### Multi-turn Conversations

Talos maintains context across the conversation:

```
>> Analyze sentiment for "DeFi protocols"
>> What are the main concerns mentioned?
>> How should we address these concerns in our next update?
>> Draft a response strategy
```

## Available Commands

### Protocol Management

```
>> Check treasury performance
>> Analyze staking metrics
>> Review governance proposals
>> Calculate optimal APR
```

### Community Engagement

```
>> What's the community saying about our protocol?
>> Analyze Twitter sentiment for "our_protocol_name"
>> Check for mentions and discussions
>> Draft a community update
```

### Development Oversight

```
>> Review open GitHub PRs
>> Check for security issues in recent commits
>> Analyze code quality metrics
>> Review contributor activity
```

### Market Analysis

```
>> What are current DeFi trends?
>> Analyze competitor protocols
>> Check yield farming opportunities
>> Review market volatility
```

## Advanced Features

### Context Awareness

Talos remembers previous conversations and can reference earlier topics:

```
>> Remember our discussion about APR optimization yesterday?
>> Based on our previous analysis, what's changed?
>> Update the recommendations from our last conversation
```

### Multi-step Workflows

Break complex tasks into steps:

```
>> I need to prepare for the governance vote next week
>> First, analyze community sentiment
>> Then review the proposal details
>> Finally, prepare talking points for the discussion
```

### Real-time Updates

Get live updates during long-running operations:

```
>> Start monitoring Twitter for protocol mentions
>> Analyze the next 100 tweets about DeFi
>> Keep me updated on any significant sentiment changes
```

## Conversation Management

### History

Talos maintains conversation history within the session:

- Previous queries and responses are remembered
- Context is preserved across multiple exchanges
- You can reference earlier parts of the conversation

### Memory

Important information is stored in persistent memory:

- Key insights and decisions
- Protocol-specific information
- User preferences and patterns
- Historical analysis results

### Session Control

```
>> clear history          # Clear current session history
>> save conversation      # Save important parts to memory
>> load previous session  # Reference previous conversations
```

## Interactive Commands

### Help and Information

```
>> help                   # General help
>> what can you do?       # Capability overview
>> show available commands # Command reference
>> explain [topic]        # Detailed explanations
```

### Status and Monitoring

```
>> status                 # System status
>> check connections      # API connectivity
>> show recent activity   # Recent operations
>> monitor [service]      # Real-time monitoring
```

### Configuration

```
>> show config           # Current configuration
>> set preference [key] [value]  # Update preferences
>> reset settings        # Reset to defaults
```

## Best Practices

### Effective Communication

**Be Specific**: Provide clear, specific requests
```
Good: "Analyze Twitter sentiment for 'yield farming' in the last 24 hours"
Poor: "Check Twitter"
```

**Provide Context**: Give relevant background information
```
Good: "We're considering increasing APR from 5% to 7%. Analyze community sentiment about yield changes."
Poor: "Should we change APR?"
```

**Ask Follow-up Questions**: Dig deeper into analysis
```
>> What are the main risks identified?
>> How confident are you in this recommendation?
>> What additional data would improve this analysis?
```

### Workflow Optimization

**Use Natural Language**: Don't worry about exact command syntax
```
>> "Can you help me understand the latest governance proposal?"
>> "I need to review PRs that might have security issues"
>> "What's the community mood about our recent changes?"
```

**Combine Operations**: Request multiple related tasks
```
>> "Analyze market sentiment, check our GitHub activity, and recommend any protocol adjustments"
```

**Iterate and Refine**: Build on previous responses
```
>> "That analysis is helpful. Can you focus specifically on the security concerns?"
>> "Based on that sentiment data, what's our best response strategy?"
```

### Session Management

**Save Important Results**: Preserve key insights
```
>> "Save this analysis to memory for future reference"
>> "Remember this decision for next week's review"
```

**Reference Previous Work**: Build on past conversations
```
>> "Based on last week's sentiment analysis, what's changed?"
>> "Update the recommendations from our previous discussion"
```

## Troubleshooting

### Common Issues

**No Response**: Check API key configuration
```
>> status
>> check connections
```

**Slow Responses**: Large queries may take time
```
>> "This is taking a while, can you give me a status update?"
```

**Unclear Results**: Ask for clarification
```
>> "Can you explain that recommendation in more detail?"
>> "What data did you use for this analysis?"
```

### Error Recovery

**Connection Issues**: Talos will attempt to reconnect automatically
```
>> "I see there was a connection issue. Can you retry that analysis?"
```

**Invalid Requests**: Talos will ask for clarification
```
>> "I'm not sure what you mean. Can you rephrase that request?"
```

### Getting Help

```
>> help                    # General help
>> troubleshoot           # Common issues
>> contact support        # How to get additional help
```

Interactive mode provides the most natural and powerful way to work with Talos, enabling sophisticated protocol management through conversational AI.
