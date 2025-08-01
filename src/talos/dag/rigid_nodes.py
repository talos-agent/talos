from __future__ import annotations

import hashlib
from typing import Any, Dict

from langchain_core.messages import AIMessage
from pydantic import BaseModel, ConfigDict

from talos.dag.nodes import DAGNode, GraphState

pass


class NodeVersion(BaseModel):
    """Version information for rigid nodes."""
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible_with(self, other: "NodeVersion") -> bool:
        """Check if this version is compatible with another version."""
        return self.major == other.major
    
    def is_newer_than(self, other: "NodeVersion") -> bool:
        """Check if this version is newer than another version."""
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch


class RigidSupportAgentNode(DAGNode):
    """
    Rigid support agent node with versioning and upgrade capabilities.
    Designed for blockchain-native individual component upgrades.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    support_agent: Any
    node_version: NodeVersion
    node_type: str = "rigid_support_agent"
    upgrade_policy: str = "compatible"
    node_hash: str = ""
    
    def __init__(self, **data):
        super().__init__(**data)
        self.node_hash = self._calculate_node_hash()
    
    def _calculate_node_hash(self) -> str:
        """Calculate deterministic hash for this node."""
        node_data = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "version": str(self.node_version),
            "domain": getattr(self.support_agent, 'domain', ''),
            "architecture": getattr(self.support_agent, 'architecture', {})
        }
        import json
        node_json = json.dumps(node_data, sort_keys=True)
        return hashlib.sha256(node_json.encode()).hexdigest()[:16]
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute the support agent with rigid architecture."""
        query = state["current_query"]
        context = state.get("context", {})
        
        context["node_version"] = str(self.node_version)
        context["node_id"] = self.node_id
        context["node_hash"] = self.node_hash
        
        enhanced_context = self.support_agent.analyze_task(query, context)
        result = self.support_agent.execute_task(enhanced_context)
        
        state["results"][self.node_id] = result
        state["messages"].append(
            AIMessage(content=f"Rigid agent {self.name} v{self.node_version} executed: {str(result)[:100]}...")
        )
        
        state["metadata"][f"{self.node_id}_execution"] = {
            "version": str(self.node_version),
            "domain": self.support_agent.domain,
            "architecture": self.support_agent.architecture,
            "node_hash": self.node_hash
        }
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        """Return enhanced configuration for blockchain serialization."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "version": str(self.node_version),
            "upgrade_policy": self.upgrade_policy,
            "node_hash": self.node_hash,
            "support_agent_config": {
                "domain": self.support_agent.domain,
                "architecture": self.support_agent.architecture,
                "delegation_keywords": self.support_agent.delegation_keywords,
                "task_patterns": self.support_agent.task_patterns
            },
            "metadata": self.metadata
        }
    
    def can_upgrade_to(self, new_version: NodeVersion) -> bool:
        """Check if this node can be upgraded to a new version."""
        if self.upgrade_policy == "exact":
            return new_version == self.node_version
        elif self.upgrade_policy == "compatible":
            return new_version.is_compatible_with(self.node_version) and new_version.is_newer_than(self.node_version)
        elif self.upgrade_policy == "any":
            return True
        return False


class RigidRouterNode(DAGNode):
    """
    Rigid router node with deterministic hash-based delegation.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    delegation_rules: Dict[str, str]
    delegation_hash: str = ""
    node_type: str = "rigid_router"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.delegation_hash = self._calculate_delegation_hash()
    
    def _calculate_delegation_hash(self) -> str:
        """Calculate deterministic hash for delegation rules."""
        import json
        rules_json = json.dumps(self.delegation_rules, sort_keys=True)
        return hashlib.sha256(rules_json.encode()).hexdigest()[:16]
    
    def execute(self, state: GraphState) -> GraphState:
        """Determine the next node based on deterministic routing logic."""
        query = state["current_query"].lower()
        
        next_node = None
        for keyword, target_node in self.delegation_rules.items():
            if keyword in query:
                next_node = target_node
                break
        
        state["context"]["next_node"] = next_node or "default"
        state["results"][self.node_id] = f"Routed to: {next_node or 'default'}"
        state["metadata"][f"{self.node_id}_routing"] = {
            "delegation_hash": self.delegation_hash,
            "matched_keyword": next((k for k in self.delegation_rules.keys() if k in query), None),
            "target_node": next_node
        }
        
        state["messages"].append(
            AIMessage(content=f"Rigid router {self.name} determined path: {next_node or 'default'}")
        )
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        """Return configuration for blockchain serialization."""
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "delegation_rules": self.delegation_rules,
            "delegation_hash": self.delegation_hash,
            "metadata": self.metadata
        }
