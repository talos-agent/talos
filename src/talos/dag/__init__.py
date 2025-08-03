"""
Talos DAG Module

This module implements a DAG (Directed Acyclic Graph) architecture for the Talos AI agent,
using LangGraph's memory and tools patterns for centralized state management and tool execution.

The DAG architecture supports various node types:
- Data sources (databases, APIs, files)
- Agents (specialized AI agents for specific tasks)
- Prompts (dynamic prompt generation and management)
- Tools (LangGraph-integrated tools and APIs)
- Services (backend services and integrations)
- Skills (specialized capabilities and workflows)

Key features:
- LangGraph-centric architecture with checkpointer memory
- Thread-based conversation tracking
- Integrated tool execution with LangGraph ToolNode
- Modular design with pluggable node types
- On-chain representation and storage
- State management and context passing between nodes
"""

from talos.dag.dag_agent import DAGAgent
from talos.dag.graph import TalosDAG
from talos.dag.manager import DAGManager
from talos.dag.nodes import (
    DAGNode,
    AgentNode,
    SkillNode,
    ServiceNode,
    ToolNode,
    DataSourceNode,
    PromptNode,
    RouterNode,
    GraphState,
)
from talos.dag.extensible_nodes import ExtensibleSkillNode, ConfigurableAgentNode
from talos.dag.extensible_manager import ExtensibleDAGManager
from talos.dag.structured_nodes import StructuredSupportAgentNode, StructuredRouterNode, NodeVersion
from talos.dag.structured_manager import StructuredDAGManager

try:
    PromptNode.model_rebuild()
except Exception:
    pass

__all__ = [
    "DAGAgent",
    "TalosDAG",
    "DAGManager",
    "DAGNode",
    "AgentNode",
    "SkillNode",
    "ServiceNode",
    "ToolNode",
    "DataSourceNode",
    "PromptNode",
    "RouterNode",
    "GraphState",
    "ExtensibleSkillNode",
    "ConfigurableAgentNode",
    "ExtensibleDAGManager",
    "StructuredSupportAgentNode",
    "StructuredRouterNode",
    "NodeVersion",
    "StructuredDAGManager",
]
