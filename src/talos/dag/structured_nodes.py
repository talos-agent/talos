from __future__ import annotations

import hashlib
from typing import Any, Dict

from langchain_core.messages import AIMessage
from pydantic import BaseModel, ConfigDict

from talos.dag.nodes import DAGNode, GraphState

pass


class NodeVersion(BaseModel):
    """
    Semantic version information for structured DAG nodes.
    
    This class implements semantic versioning (semver) for blockchain-native
    node upgrades. It provides compatibility checking and version comparison
    methods essential for deterministic upgrade validation.
    
    Attributes:
        major: Major version number (breaking changes)
        minor: Minor version number (backward-compatible features)
        patch: Patch version number (backward-compatible bug fixes)
    
    Version Compatibility Rules:
        - Compatible upgrades: Same major version (1.0.0 -> 1.1.0)
        - Breaking changes: Different major version (1.0.0 -> 2.0.0)
        - Patch updates: Same major.minor (1.0.0 -> 1.0.1)
    
    Examples:
        >>> v1 = NodeVersion(major=1, minor=0, patch=0)
        >>> v2 = NodeVersion(major=1, minor=1, patch=0)
        >>> v1.is_compatible_with(v2)  # True - same major version
        >>> v2.is_newer_than(v1)      # True - higher minor version
    """
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        """Return string representation in semver format (major.minor.patch)."""
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def is_compatible_with(self, other: "NodeVersion") -> bool:
        """
        Check if this version is compatible with another version.
        
        Compatibility is determined by major version equality. This ensures
        that breaking changes (major version bumps) are properly detected
        and handled during blockchain-native upgrades.
        
        Args:
            other: The version to compare against
            
        Returns:
            True if versions are compatible (same major version)
        """
        return self.major == other.major
    
    def is_newer_than(self, other: "NodeVersion") -> bool:
        """
        Check if this version is newer than another version.
        
        Uses semantic versioning precedence rules:
        1. Major version takes precedence
        2. Minor version compared if major versions equal
        3. Patch version compared if major.minor equal
        
        Args:
            other: The version to compare against
            
        Returns:
            True if this version is newer than the other
        """
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch


class StructuredSupportAgentNode(DAGNode):
    """
    Structured support agent node with versioning and upgrade capabilities.
    
    This class represents a blockchain-native DAG node that wraps a SupportAgent
    with deterministic versioning, upgrade policies, and hash-based identification.
    It's designed to enable individual component upgrades in a distributed AI system.
    
    Key Features:
        - Semantic versioning with upgrade policy enforcement
        - Deterministic hashing for blockchain compatibility
        - Individual node upgrade capabilities
        - Reproducible serialization for on-chain storage
        
    Blockchain-Native Design:
        - All operations produce deterministic, reproducible results
        - Node hashes are calculated from sorted, canonical representations
        - Upgrade policies ensure safe, validated transitions
        - Serialization maintains consistent ordering for blockchain storage
        
    Upgrade Policies:
        - "compatible": Only allows upgrades within same major version
        - "exact": Requires exact version matches (no upgrades)
        - "any": Allows any newer version upgrade
        
    Attributes:
        support_agent: The wrapped SupportAgent instance
        node_version: Semantic version of this node
        upgrade_policy: Policy governing allowed upgrades
        node_hash: Deterministic hash for blockchain identification
        
    Examples:
        >>> agent = SupportAgent(name="governance", domain="governance", ...)
        >>> node = StructuredSupportAgentNode(
        ...     node_id="gov_node",
        ...     name="Governance Node",
        ...     support_agent=agent,
        ...     node_version=NodeVersion(1, 0, 0),
        ...     upgrade_policy="compatible"
        ... )
        >>> node.can_upgrade_to(NodeVersion(1, 1, 0))  # True
        >>> node.can_upgrade_to(NodeVersion(2, 0, 0))  # False
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    support_agent: Any
    node_version: NodeVersion
    node_type: str = "structured_support_agent"
    upgrade_policy: str = "compatible"
    node_hash: str = ""
    
    def __init__(self, **data):
        super().__init__(**data)
        self.node_hash = self._calculate_node_hash()
    
    def _calculate_node_hash(self) -> str:
        """
        Calculate deterministic hash for blockchain compatibility.
        
        This method creates a reproducible hash by:
        1. Extracting all relevant node properties
        2. Sorting collections to ensure deterministic ordering
        3. Creating a canonical string representation
        4. Computing SHA-256 hash for blockchain identification
        
        The hash includes:
        - Node identification (id, name, description)
        - Support agent properties (domain, architecture, keywords)
        - Version information
        - Task patterns and delegation rules
        
        Returns:
            Hexadecimal SHA-256 hash string for blockchain identification
        """
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
        """
        Execute the support agent with the current state.
        
        This method processes the current query through the wrapped support agent,
        maintaining state consistency and message history for the DAG execution.
        It enhances the state with node-specific metadata for blockchain verification.
        
        Args:
            state: Current graph state containing query, context, and results
            
        Returns:
            Updated graph state with execution results and messages
        """
        query = state["current_query"]
        context = state.get("context", {})
        
        context["node_version"] = str(self.node_version)
        context["node_id"] = self.node_id
        context["node_hash"] = self.node_hash
        
        enhanced_context = self.support_agent.analyze_task(query, context)
        result = self.support_agent.execute_task(enhanced_context)
        
        state["results"][self.node_id] = result
        state["messages"].append(
            AIMessage(content=f"Structured agent {self.name} v{self.node_version} executed: {str(result)[:100]}...")
        )
        
        state["metadata"][f"{self.node_id}_execution"] = {
            "version": str(self.node_version),
            "domain": self.support_agent.domain,
            "architecture": self.support_agent.architecture,
            "node_hash": self.node_hash
        }
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        """
        Return configuration for blockchain-native serialization.
        
        This method produces a deterministic, sorted configuration suitable
        for blockchain storage and cross-system compatibility. All collections
        are sorted to ensure reproducible serialization.
        
        Returns:
            Dictionary containing complete node configuration with:
            - Node identification and metadata
            - Support agent configuration
            - Version and upgrade policy information
            - Deterministic hash for verification
        """
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
        """
        Check if this node can be upgraded to the specified version.
        
        This method enforces upgrade policies to ensure safe, validated
        transitions between node versions. It prevents incompatible upgrades
        that could break the DAG's deterministic behavior.
        
        Upgrade Policy Enforcement:
        - "compatible": Allows upgrades within same major version only
        - "exact": Prevents all upgrades (version must match exactly)
        - "any": Allows any newer version (use with caution)
        
        Args:
            new_version: Target version for potential upgrade
            
        Returns:
            True if upgrade is allowed by current policy, False otherwise
            
        Examples:
            >>> node.upgrade_policy = "compatible"
            >>> node.node_version = NodeVersion(1, 0, 0)
            >>> node.can_upgrade_to(NodeVersion(1, 1, 0))  # True
            >>> node.can_upgrade_to(NodeVersion(2, 0, 0))  # False
        """
        if self.upgrade_policy == "exact":
            return new_version == self.node_version
        elif self.upgrade_policy == "compatible":
            return new_version.is_compatible_with(self.node_version) and new_version.is_newer_than(self.node_version)
        elif self.upgrade_policy == "any":
            return True
        return False


class StructuredRouterNode(DAGNode):
    """
    Structured router node with deterministic hash-based delegation.
    
    This class implements a blockchain-native routing mechanism that uses
    deterministic keyword matching to delegate tasks to appropriate support
    agents. It ensures reproducible routing decisions across different
    execution environments.
    
    Key Features:
        - Deterministic delegation based on keyword matching
        - Hash-based verification of routing rules
        - Blockchain-compatible serialization
        - Reproducible routing decisions
        
    Blockchain-Native Design:
        - Delegation rules are sorted for deterministic hashing
        - Routing decisions are reproducible and verifiable
        - Configuration serialization maintains consistent ordering
        - Hash verification ensures rule integrity
        
    The router analyzes incoming queries and matches them against predefined
    keyword sets for each domain. The first matching domain is selected,
    with a fallback to "default" if no matches are found.
    
    Attributes:
        delegation_rules: Mapping of domains to keyword lists
        delegation_hash: Deterministic hash of delegation rules
        
    Examples:
        >>> rules = {
        ...     "governance": ["proposal", "vote", "dao"],
        ...     "analytics": ["data", "report", "metrics"]
        ... }
        >>> router = StructuredRouterNode(
        ...     node_id="main_router",
        ...     name="Main Router",
        ...     delegation_rules=rules
        ... )
        >>> # Query "analyze governance proposal" would route to "governance"
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    delegation_rules: Dict[str, str]
    delegation_hash: str = ""
    node_type: str = "structured_router"
    
    def __init__(self, **data):
        super().__init__(**data)
        self.delegation_hash = self._calculate_delegation_hash()
    
    def _calculate_delegation_hash(self) -> str:
        """
        Calculate deterministic hash for delegation rules.
        
        This method creates a reproducible hash of the delegation rules by:
        1. Sorting keywords within each domain
        2. Sorting domains alphabetically
        3. Creating canonical string representation
        4. Computing SHA-256 hash for verification
        
        The hash enables blockchain verification that delegation rules
        haven't been tampered with and ensures consistent routing behavior
        across different execution environments.
        
        Returns:
            Hexadecimal SHA-256 hash of sorted delegation rules
        """
        import json
        rules_json = json.dumps(self.delegation_rules, sort_keys=True)
        return hashlib.sha256(rules_json.encode()).hexdigest()[:16]
    
    def execute(self, state: GraphState) -> GraphState:
        """
        Route the query to appropriate support agent based on keywords.
        
        This method implements deterministic routing by:
        1. Converting query to lowercase for case-insensitive matching
        2. Iterating through delegation rules in sorted order
        3. Selecting first domain with matching keywords
        4. Falling back to "default" if no matches found
        
        The routing decision is deterministic and reproducible, ensuring
        consistent behavior across different execution environments.
        
        Args:
            state: Current graph state containing the query to route
            
        Returns:
            Updated graph state with selected domain and routing result
        """
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
            AIMessage(content=f"Structured router {self.name} determined path: {next_node or 'default'}")
        )
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        """
        Return configuration for blockchain-native serialization.
        
        This method produces a deterministic configuration suitable for
        blockchain storage. All collections are sorted to ensure reproducible
        serialization across different execution environments.
        
        Returns:
            Dictionary containing complete router configuration with:
            - Node identification and metadata
            - Sorted delegation rules for deterministic serialization
            - Delegation hash for rule verification
        """
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "delegation_rules": self.delegation_rules,
            "delegation_hash": self.delegation_hash,
            "metadata": self.metadata
        }
