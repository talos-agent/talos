# Structured DAG Framework Tutorial

## Overview

The Structured DAG Framework is a blockchain-native AI system that enables individual component upgrades while maintaining deterministic behavior and system integrity. It orchestrates a network of specialized support agents through a structured Directed Acyclic Graph (DAG) architecture.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Key Concepts](#key-concepts)
3. [Getting Started](#getting-started)
4. [Node Versioning](#node-versioning)
5. [Upgrade Workflows](#upgrade-workflows)
6. [Blockchain Integration](#blockchain-integration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Architecture Overview

### Blockchain-Native Design

The framework is designed from the ground up for blockchain compatibility:

- **Deterministic Execution**: All operations produce reproducible results
- **Individual Node Upgrades**: Enable granular system evolution
- **Hash-based Verification**: Prevents tampering and ensures integrity
- **Serializable State**: Enables on-chain storage and verification

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    StructuredMainAgent                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │ StructuredDAG   │    │    SupportAgent Registry       │ │
│  │    Manager      │    │                                 │ │
│  │                 │    │  ┌─────────────┐ ┌─────────────┐│ │
│  │ • Node Upgrades │    │  │ Governance  │ │ Analytics   ││ │
│  │ • Version Mgmt  │    │  │   Agent     │ │   Agent     ││ │
│  │ • Serialization │    │  │             │ │             ││ │
│  └─────────────────┘    │  └─────────────┘ └─────────────┘│ │
└─────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Structured DAG                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Router    │  │  Support    │  │    Prompt/Data      │  │
│  │    Node     │  │   Agent     │  │      Nodes          │  │
│  │             │  │   Nodes     │  │                     │  │
│  │ • Keywords  │  │             │  │ • Shared Resources  │  │
│  │ • Hash-based│  │ • Versioned │  │ • Deterministic     │  │
│  │ • Routing   │  │ • Upgradeable│  │ • Configurable      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Key Concepts

### Support Agents

Support agents are specialized AI components with specific domain expertise:

- **Domain-Specific**: Each agent handles a particular area (governance, analytics, etc.)
- **Versioned**: Individual semantic versioning for controlled upgrades
- **Configurable**: Custom architectures and delegation patterns
- **Isolated**: Independent upgrade paths without affecting other agents

### Node Versioning

The framework uses semantic versioning (major.minor.patch) with three upgrade policies:

- **Compatible**: Only allows upgrades within the same major version
- **Exact**: Requires exact version matches (no upgrades allowed)
- **Any**: Allows any newer version upgrade (use with caution)

### Deterministic Delegation

Task routing uses deterministic patterns:

- **Keyword Matching**: Sorted rule evaluation for reproducible results
- **Hash Verification**: Ensures delegation rules haven't been tampered with
- **Fallback Mechanisms**: Default routing for unmatched queries

## Getting Started

### Basic Setup

```python
from langchain_openai import ChatOpenAI
from talos.core.extensible_agent import StructuredMainAgent
from talos.dag.structured_nodes import NodeVersion
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager

# Initialize the structured agent
model = ChatOpenAI(model="gpt-4")
prompt_manager = FilePromptManager("/path/to/prompts")

agent = StructuredMainAgent(
    model=model,
    prompts_dir="/path/to/prompts",
    prompt_manager=prompt_manager,
    verbose=True,
    use_database_memory=False
)
```

### Creating Custom Support Agents

```python
from talos.core.extensible_agent import SupportAgent

# Define a custom support agent
custom_agent = SupportAgent(
    name="security",
    domain="security",
    description="Security analysis and validation agent",
    architecture={
        "task_flow": ["scan", "analyze", "validate", "report"],
        "decision_points": ["threat_level", "validation_method", "response_action"],
        "capabilities": ["vulnerability_scanning", "threat_analysis", "compliance_check"]
    },
    delegation_keywords=["security", "vulnerability", "threat", "compliance"],
    task_patterns=["scan for vulnerabilities", "analyze threats", "validate security"]
)
```

## Node Versioning

### Version Compatibility

```python
from talos.dag.structured_nodes import NodeVersion

# Create versions
v1_0_0 = NodeVersion(major=1, minor=0, patch=0)
v1_1_0 = NodeVersion(major=1, minor=1, patch=0)
v2_0_0 = NodeVersion(major=2, minor=0, patch=0)

# Check compatibility
print(v1_0_0.is_compatible_with(v1_1_0))  # True - same major version
print(v1_0_0.is_compatible_with(v2_0_0))  # False - different major version
print(v1_1_0.is_newer_than(v1_0_0))      # True - higher minor version
```

### Upgrade Policies

```python
# Compatible policy - allows upgrades within same major version
node.upgrade_policy = "compatible"
node.can_upgrade_to(NodeVersion(1, 1, 0))  # True if current is 1.0.0
node.can_upgrade_to(NodeVersion(2, 0, 0))  # False - major version change

# Exact policy - no upgrades allowed
node.upgrade_policy = "exact"
node.can_upgrade_to(NodeVersion(1, 0, 1))  # False - any change blocked

# Any policy - allows any newer version
node.upgrade_policy = "any"
node.can_upgrade_to(NodeVersion(2, 0, 0))  # True - any upgrade allowed
```

## Upgrade Workflows

### Individual Node Upgrades

```python
# 1. Validate upgrade compatibility
validation = agent.validate_upgrade("governance", NodeVersion(1, 1, 0))
if not validation["valid"]:
    print(f"Upgrade blocked: {validation['reason']}")
    exit()

# 2. Create enhanced agent
enhanced_agent = SupportAgent(
    name="governance_v2",
    domain="governance",
    description="Enhanced governance with improved consensus",
    architecture={
        "task_flow": ["validate", "analyze", "simulate", "execute", "confirm"],
        "decision_points": ["proposal_validity", "consensus_mechanism", "execution_safety", "rollback_plan"],
        "capabilities": ["proposal_validation", "consensus_coordination", "safe_execution", "simulation"]
    },
    delegation_keywords=["governance", "proposal", "vote", "consensus", "dao"],
    task_patterns=["validate proposal", "coordinate consensus", "execute governance", "simulate outcome"]
)

# 3. Perform upgrade
success = agent.upgrade_support_agent(
    "governance",
    enhanced_agent,
    NodeVersion(1, 1, 0)
)

if success:
    print("Upgrade completed successfully")
else:
    print("Upgrade failed")
```

### Rollback Operations

```python
# Rollback to previous version
success = agent.rollback_node("governance", NodeVersion(1, 0, 0))
if success:
    print("Rollback completed successfully")
else:
    print("Rollback failed - version may be newer than current")
```

### System Status Monitoring

```python
# Get comprehensive system status
status = agent.get_structured_status()
print(f"DAG has {status['total_nodes']} nodes")
print(f"Blockchain ready: {status['blockchain_ready']}")

for node_id, info in status['structured_nodes'].items():
    print(f"{node_id}: v{info['version']} (policy: {info['upgrade_policy']})")

# Get individual node status
node_status = agent.get_node_status("governance")
print(f"Governance agent v{node_status['version']}")
print(f"Node hash: {node_status['node_hash']}")
print(f"Keywords: {node_status['delegation_keywords']}")
```

## Blockchain Integration

### Deterministic Serialization

The framework ensures all operations produce deterministic, reproducible results:

```python
# Export DAG for blockchain storage
blockchain_data = agent.export_for_blockchain()
print(f"DAG version: {blockchain_data.get('dag_version')}")
print(f"Checksum: {blockchain_data.get('checksum')}")
print(f"Nodes: {len(blockchain_data.get('nodes', {}))}")
```

### Hash-based Verification

All components include deterministic hashes for integrity verification:

- **Node Hashes**: Calculated from sorted node properties
- **Delegation Hashes**: Verify routing rule integrity
- **DAG Checksums**: Overall system integrity verification

### On-chain Storage Format

The export format is optimized for blockchain storage:

```json
{
  "dag_version": "1.0.0",
  "checksum": "a1b2c3d4e5f6...",
  "nodes": {
    "governance_agent": {
      "version": "1.1.0",
      "hash": "f6e5d4c3b2a1...",
      "config": {...}
    }
  },
  "edges": [...],
  "delegation_rules": {...}
}
```

## Best Practices

### Version Management

1. **Use Semantic Versioning**: Follow semver principles for clear upgrade paths
2. **Test Upgrades**: Validate compatibility before production upgrades
3. **Document Changes**: Maintain clear upgrade documentation
4. **Gradual Rollouts**: Test upgrades in staging environments first

### Security Considerations

1. **Hash Verification**: Always verify node and delegation hashes
2. **Upgrade Validation**: Use appropriate upgrade policies for your use case
3. **Rollback Planning**: Maintain rollback capabilities for critical systems
4. **Access Control**: Implement proper permissions for upgrade operations

### Performance Optimization

1. **Selective Upgrades**: Only upgrade nodes that need changes
2. **Batch Operations**: Group related upgrades when possible
3. **Hash Caching**: Leverage deterministic hashes for verification
4. **Minimal Rebuilds**: Only rebuild affected DAG components

### Monitoring and Observability

1. **Status Monitoring**: Regularly check system status
2. **Version Tracking**: Monitor node versions and upgrade history
3. **Hash Verification**: Validate integrity through hash checking
4. **Performance Metrics**: Track upgrade and execution performance

## Troubleshooting

### Common Issues

#### Upgrade Validation Failures

**Problem**: Node upgrade fails with "Incompatible version" error

**Solution**:
```python
# Check current upgrade policy
status = agent.get_node_status("governance")
print(f"Current policy: {status['upgrade_policy']}")

# Validate upgrade before attempting
validation = agent.validate_upgrade("governance", NodeVersion(2, 0, 0))
if not validation["valid"]:
    print(f"Reason: {validation['reason']}")
    
# Consider using force upgrade if necessary (use with caution)
success = agent.upgrade_support_agent(
    "governance", 
    new_agent, 
    NodeVersion(2, 0, 0),
    force=True
)
```

#### DAG Construction Failures

**Problem**: Structured DAG fails to build

**Solution**:
```python
# Check for missing dependencies
try:
    agent._build_structured_dag()
except Exception as e:
    print(f"DAG build error: {e}")
    # Check prompt manager and model configuration
```

#### Hash Mismatches

**Problem**: Node hashes don't match expected values

**Solution**:
```python
# Recalculate node hash
node = agent.structured_dag_manager.node_registry["governance"]
expected_hash = node._calculate_node_hash()
print(f"Expected hash: {expected_hash}")
print(f"Current hash: {node.node_hash}")
```

### Debugging Tips

1. **Enable Verbose Mode**: Set `verbose=True` when creating agents
2. **Check Status Regularly**: Use `get_structured_status()` for system overview
3. **Validate Before Upgrading**: Always run `validate_upgrade()` first
4. **Monitor CI/CD**: Ensure all checks pass before deployment

## Advanced Usage

### Custom Upgrade Policies

```python
# Create node with custom upgrade policy
custom_node = StructuredSupportAgentNode(
    node_id="custom_agent",
    name="Custom Agent",
    support_agent=custom_agent,
    node_version=NodeVersion(1, 0, 0),
    upgrade_policy="exact"  # No upgrades allowed
)
```

### Blockchain Integration

```python
# Export for blockchain storage
blockchain_data = agent.export_for_blockchain()

# Store on blockchain (pseudo-code)
blockchain_client.store_dag_config(
    config=blockchain_data,
    checksum=blockchain_data["checksum"]
)

# Verify integrity
stored_config = blockchain_client.retrieve_dag_config()
assert stored_config["checksum"] == blockchain_data["checksum"]
```

### Multi-Environment Deployment

```python
# Development environment
dev_agent = StructuredMainAgent(
    model=ChatOpenAI(model="gpt-3.5-turbo"),
    prompts_dir="/dev/prompts",
    verbose=True
)

# Production environment
prod_agent = StructuredMainAgent(
    model=ChatOpenAI(model="gpt-4"),
    prompts_dir="/prod/prompts",
    verbose=False
)

# Ensure consistent configuration
dev_status = dev_agent.get_structured_status()
prod_status = prod_agent.get_structured_status()
assert dev_status["delegation_hash"] == prod_status["delegation_hash"]
```

## API Reference

### StructuredMainAgent

The main entry point for the structured DAG framework.

#### Methods

- `upgrade_support_agent(domain, new_agent, new_version, force=False)`: Upgrade individual node
- `validate_upgrade(domain, new_version)`: Validate upgrade compatibility
- `rollback_node(domain, target_version)`: Rollback to previous version
- `get_node_status(domain)`: Get detailed node information
- `get_structured_status()`: Get comprehensive system status
- `export_for_blockchain()`: Export for blockchain storage
- `delegate_task(query, context=None)`: Execute task through DAG

### NodeVersion

Semantic versioning for DAG nodes.

#### Methods

- `is_compatible_with(other)`: Check version compatibility
- `is_newer_than(other)`: Compare version precedence
- `__str__()`: String representation (major.minor.patch)

### StructuredSupportAgentNode

Individual DAG node with versioning capabilities.

#### Methods

- `can_upgrade_to(new_version)`: Check upgrade eligibility
- `execute(state)`: Process graph state
- `get_node_config()`: Get serializable configuration
- `_calculate_node_hash()`: Generate deterministic hash

### StructuredDAGManager

Manager for DAG operations and upgrades.

#### Methods

- `create_structured_dag(...)`: Build deterministic DAG
- `upgrade_node(domain, new_agent, new_version, force=False)`: Perform node upgrade
- `validate_upgrade(domain, new_version)`: Validate upgrade request
- `rollback_node(domain, target_version)`: Rollback node version
- `get_structured_dag_status()`: Get comprehensive DAG status
- `export_for_blockchain()`: Export DAG configuration

## Conclusion

The Structured DAG Framework provides a robust foundation for blockchain-native AI systems with individual component upgrades. By following the patterns and best practices outlined in this tutorial, you can build scalable, maintainable AI systems that evolve safely over time.

Key takeaways:

1. **Deterministic Design**: All operations produce reproducible results
2. **Individual Upgrades**: Components can be upgraded independently
3. **Version Safety**: Semantic versioning prevents breaking changes
4. **Blockchain Ready**: Built for on-chain deployment and verification
5. **Comprehensive Monitoring**: Full visibility into system state and health

For additional support and examples, refer to the demo script and test cases in the repository.
