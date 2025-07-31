"""
Talos DAG (Directed Acyclic Graph) module for LangGraph-based agent architecture.

This module provides a DAG-based approach to agent execution where nodes can be:
- Data sources (DatasetManager, external APIs)
- Agents (specialized AI agents for different tasks)
- Prompts (prompt templates and management)
- Tools (external integrations and utilities)
- Services (business logic implementations)
- Skills (LLM-driven capabilities)

The DAG architecture enables:
- Modular and extensible agent design
- Proposal-based architecture modifications
- On-chain representation of agent structure
- Supervised execution with hypervisor integration
"""

from talos.dag.dag_agent import DAGAgent
from talos.dag.graph import TalosDAG, DAGProposal
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
from talos.dag.proposal_skill import DAGProposalSkill, DAGProposalResult

__all__ = [
    "DAGAgent",
    "TalosDAG",
    "DAGProposal",
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
    "DAGProposalSkill",
    "DAGProposalResult",
]
