# Core Components

Talos is comprised of several key components that allow it to function as a decentralized AI protocol owner.

## System Architecture

The codebase follows a layered architecture with clear separation of concerns:

```
src/talos/
├── core/           # Core agent system and orchestration
├── skills/         # Modular capabilities (sentiment analysis, proposals, etc.)
├── services/       # Business logic implementations  
├── tools/          # External API integrations and utilities
├── hypervisor/     # Action supervision and approval system
├── prompts/        # LLM prompt templates and management
├── cli/            # Command-line interface
├── data/           # Data management and vector storage
├── models/         # Pydantic data models
└── utils/          # Utility functions and clients
```

## Core Components

### Hypervisor and Supervisor

The **Hypervisor** is the core of Talos's governance capabilities. It monitors all actions and uses a Supervisor to approve or deny them based on a set of rules and the agent's history. This protects the protocol from malicious or erroneous actions.

**Key Features:**
- Monitors all agent actions in real-time
- Rule-based approval/denial system
- Maintains audit trails of all decisions
- Integrates with LLM prompts for complex decision making
- Supports multiple supervisor implementations

**Components:**
- `Hypervisor` - Main monitoring and coordination system
- `Supervisor` - Abstract interface for approval logic
- `RuleBasedSupervisor` - Concrete implementation with configurable rules

### Proposal Evaluation System

Talos can systematically evaluate governance proposals, providing detailed analysis to help stakeholders make informed decisions.

**Capabilities:**
- LLM-based proposal analysis
- Risk assessment and scoring
- Community feedback integration
- Recommendation generation with reasoning
- Historical proposal tracking

**Implementation:**
- `ProposalsSkill` - Main proposal evaluation logic
- Integration with external data sources
- Structured output with scoring metrics

### Tool-Based Architecture

Talos uses a variety of tools to interact with external services like Twitter, GitHub, and GitBook, allowing it to perform a wide range of tasks.

**Tool Management:**
- `ToolManager` - Central registry for all available tools
- `SupervisedTool` - Wrapper that adds approval workflow to any tool
- Dynamic tool discovery and registration
- Extensible architecture for new integrations

**Available Tools:**
- **GitHub Tools** - Repository management, PR reviews, issue tracking
- **Twitter Tools** - Social media monitoring, sentiment analysis, posting
- **IPFS Tools** - Decentralized storage and content management
- **Cryptography Tools** - Key management, encryption/decryption

## Agent System

### Main Agent

The `MainAgent` serves as the top-level orchestrator that integrates all system components:

- **Direct Skill/Service Management** - Manages skills and services directly
- **Hypervisor Integration** - Ensures all actions are supervised
- **Tool Management** - Manages available tools and their registration
- **Memory System** - Persistent conversation history and semantic search
- **Skill Coordination** - Orchestrates multiple skills for complex tasks

### Base Agent

The `Agent` class provides core functionality for all AI agents:

- **LLM Interaction** - Standardized interface to language models
- **Conversation History** - Maintains context across interactions
- **Memory Management** - Semantic search and retrieval
- **Prompt Management** - Template-based prompt system

## Data Management

### Memory System

Persistent storage with semantic search capabilities:

- **FAISS Integration** - Vector similarity search
- **Conversation History** - Maintains context across sessions
- **Metadata Support** - Rich tagging and filtering
- **Batch Operations** - Optimized for performance

### Dataset Management

Manages textual datasets with vector embeddings:

- **Vector Embeddings** - Semantic similarity search
- **FAISS Backend** - Efficient similarity queries
- **Batch Processing** - Optimized for large datasets
- **Metadata Integration** - Rich content tagging

## External Integrations

### GitHub Integration

Comprehensive GitHub API integration:

- **Repository Operations** - Clone, fork, branch management
- **Pull Request Management** - Review, approve, merge workflows
- **Issue Tracking** - Create, update, close issues
- **Code Review** - AI-powered code analysis and feedback

### Twitter Integration

Social media monitoring and engagement:

- **Content Analysis** - Sentiment analysis and trend detection
- **Account Evaluation** - Influence scoring and verification
- **Automated Posting** - Scheduled and reactive content
- **Community Monitoring** - Real-time sentiment tracking

### IPFS Integration

Decentralized storage capabilities:

- **Content Storage** - Immutable content addressing
- **Metadata Management** - Rich content descriptions
- **Pinning Services** - Reliable content availability
- **Gateway Integration** - HTTP access to IPFS content

## Configuration and Extensibility

### Prompt Management

Template-based prompt system:

- **File-based Templates** - JSON prompt definitions
- **Dynamic Loading** - Runtime prompt updates
- **Concatenation Support** - Modular prompt composition
- **Version Control** - Track prompt changes over time

### Skill System

Modular capability architecture:

- **Abstract Base Classes** - Standardized skill interface
- **Dynamic Registration** - Runtime skill discovery
- **Parameter Validation** - Type-safe skill execution
- **Result Standardization** - Consistent output formats

This architecture enables Talos to operate as a sophisticated AI protocol owner while maintaining security, extensibility, and reliability.
