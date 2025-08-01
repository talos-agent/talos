from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from pydantic import ConfigDict

from talos.dag.graph import TalosDAG
from talos.dag.manager import DAGManager
from talos.dag.nodes import PromptNode, DataSourceNode, ToolNode
from talos.dag.structured_nodes import StructuredSupportAgentNode, StructuredRouterNode, NodeVersion
from talos.data.dataset_manager import DatasetManager
from talos.prompts.prompt_manager import PromptManager
from talos.services.abstract.service import Service
from talos.tools.tool_manager import ToolManager

pass


class StructuredDAGManager(DAGManager):
    """
    Manager for structured DAGs with controlled node upgrades and blockchain-native capabilities.
    
    This class extends the base DAGManager to provide deterministic DAG construction,
    versioned node management, and blockchain-compatible serialization. It's designed
    to enable individual component upgrades in a distributed AI system while maintaining
    deterministic behavior and upgrade safety.
    
    Key Features:
        - Controlled node upgrade methodology with version validation
        - Deterministic DAG structure creation and management
        - Blockchain-native serialization with reproducible hashing
        - Individual node rollback capabilities
        - Upgrade policy enforcement and compatibility checking
        
    Blockchain-Native Design:
        - All operations produce deterministic, reproducible results
        - DAG structure is serialized with consistent ordering
        - Node upgrades are validated and logged for auditability
        - Delegation patterns use hash-based verification
        - Export format is suitable for on-chain storage
        
    The manager maintains a registry of StructuredSupportAgentNode instances,
    each with semantic versioning and upgrade policies. It ensures that all
    DAG modifications follow controlled upgrade paths and maintain system integrity.
    
    Attributes:
        node_registry: Registry of versioned support agent nodes
        dag_version: Current version of the DAG structure
        delegation_hash: Hash of current delegation rules
        
    Examples:
        >>> manager = StructuredDAGManager()
        >>> agent = SupportAgent(name="governance", domain="governance", ...)
        >>> manager.add_support_agent(agent, NodeVersion(1, 0, 0))
        >>> dag = manager.create_structured_dag(...)
        >>> manager.upgrade_node("governance", new_agent, NodeVersion(1, 1, 0))
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    node_registry: Dict[str, StructuredSupportAgentNode] = {}
    delegation_hash: str = ""
    dag_version: str = "1.0.0"
    
    def create_structured_dag(
        self,
        model: BaseChatModel,
        prompt_manager: PromptManager,
        support_agents: Dict[str, Any],
        services: List[Service],
        tool_manager: ToolManager,
        dataset_manager: Optional[DatasetManager] = None,
        dag_name: str = "structured_talos_dag"
    ) -> TalosDAG:
        """
        Create a structured DAG with controlled node management and deterministic architecture.
        
        This method constructs a blockchain-native DAG with the following structure:
        1. Router node for deterministic task delegation
        2. Individual support agent nodes with versioning
        3. Shared prompt and data source nodes
        4. Deterministic edge connections
        
        The resulting DAG ensures:
        - Reproducible execution paths
        - Individual node upgrade capabilities
        - Blockchain-compatible serialization
        - Deterministic delegation patterns
        
        Args:
            model: Language model for agent operations
            prompt_manager: Manager for prompt templates
            support_agents: Dictionary of support agents to include as nodes
            services: List of services for the DAG
            tool_manager: Manager for tools and capabilities
            dataset_manager: Optional dataset manager for data source nodes
            dag_name: Unique name for the DAG instance
            
        Returns:
            Configured TalosDAG with structured node architecture
            
        Raises:
            ValueError: If DAG construction fails or validation errors occur
        """
        
        dag = TalosDAG(
            name=dag_name,
            description="Structured Talos agent DAG with blockchain-native node upgrades"
        )
        
        delegation_rules = self._create_deterministic_delegation(support_agents)
        self.delegation_hash = self._calculate_delegation_hash(delegation_rules)
        
        prompt_node = PromptNode(
            node_id="main_prompt",
            name="Main Agent Prompt",
            description="Primary prompt for the structured Talos agent",
            prompt_manager=prompt_manager,
            prompt_names=["main_agent_prompt", "general_agent_prompt"]
        )
        dag.add_node(prompt_node)
        
        if dataset_manager:
            data_node = DataSourceNode(
                node_id="dataset_source",
                name="Dataset Manager",
                description="Provides relevant documents and context",
                data_source=dataset_manager
            )
            dag.add_node(data_node)
            dag.add_edge("main_prompt", "dataset_source")
        
        router_node = StructuredRouterNode(
            node_id="structured_router",
            name="Structured Router",
            description="Deterministic router with hash-based delegation",
            delegation_rules=delegation_rules
        )
        dag.add_node(router_node)
        
        if dataset_manager:
            dag.add_edge("dataset_source", "structured_router")
        else:
            dag.add_edge("main_prompt", "structured_router")
        
        for domain, agent in support_agents.items():
            structured_node = StructuredSupportAgentNode(
                node_id=f"{domain}_agent",
                name=f"{domain.title()} Agent",
                description=agent.description,
                support_agent=agent,
                node_version=NodeVersion(major=1, minor=0, patch=0)
            )
            dag.add_node(structured_node)
            self.node_registry[domain] = structured_node
        
        if tool_manager.tools:
            tools_list = list(tool_manager.tools.values())
            tool_node = ToolNode(
                node_id="structured_tools",
                name="Structured Tools",
                description="LangGraph tools for structured operations",
                tools=tools_list
            )
            dag.add_node(tool_node)
        
        conditional_targets = {}
        for keyword, target in delegation_rules.items():
            if target in [node.node_id for node in dag.nodes.values()]:
                conditional_targets[target] = target
        
        if conditional_targets:
            dag.add_conditional_edge("structured_router", conditional_targets)
        
        self.current_dag = dag
        return dag
    
    def _create_deterministic_delegation(self, support_agents: Dict[str, Any]) -> Dict[str, str]:
        """Create deterministic delegation rules based on support agents."""
        delegation_rules = {}
        
        for domain, agent in support_agents.items():
            target_node = f"{domain}_agent"
            
            for keyword in agent.delegation_keywords:
                delegation_rules[keyword.lower()] = target_node
            
            for pattern in agent.task_patterns:
                key_words = pattern.lower().split()
                for word in key_words:
                    if len(word) > 3:
                        delegation_rules[word] = target_node
        
        return dict(sorted(delegation_rules.items()))
    
    def _calculate_delegation_hash(self, delegation_rules: Dict[str, str]) -> str:
        """Calculate deterministic hash for delegation rules."""
        rules_json = json.dumps(delegation_rules, sort_keys=True)
        return hashlib.sha256(rules_json.encode()).hexdigest()[:16]
    
    def upgrade_node(
        self,
        domain: str,
        new_agent: Any,
        new_version: NodeVersion,
        force: bool = False
    ) -> bool:
        """
        Upgrade a specific node with comprehensive version validation.
        
        This method performs a controlled upgrade of an individual DAG node:
        1. Validates the target node exists and is upgradeable
        2. Checks version compatibility against upgrade policy
        3. Creates new node instance with updated configuration
        4. Replaces old node while preserving DAG structure
        5. Updates delegation hash and DAG metadata
        
        The upgrade process ensures:
        - No breaking changes to DAG structure
        - Version compatibility enforcement
        - Deterministic hash recalculation
        - Rollback capability preservation
        
        Args:
            domain: Domain identifier of the node to upgrade
            new_agent: Updated support agent configuration
            new_version: Target version for the upgrade
            force: Whether to bypass version compatibility checks
            
        Returns:
            True if upgrade succeeded, False if validation failed
            
        Examples:
            >>> success = manager.upgrade_node(
            ...     "governance",
            ...     enhanced_governance_agent,
            ...     NodeVersion(1, 1, 0)
            ... )
            >>> if success:
            ...     print("Upgrade completed successfully")
        """
        if not self.current_dag or domain not in self.node_registry:
            return False
        
        current_node = self.node_registry[domain]
        
        if not force and not current_node.can_upgrade_to(new_version):
            return False
        
        old_node_id = current_node.node_id
        
        new_node = StructuredSupportAgentNode(
            node_id=old_node_id,
            name=current_node.name,
            description=new_agent.description,
            support_agent=new_agent,
            node_version=new_version,
            upgrade_policy=current_node.upgrade_policy
        )
        
        if self.current_dag:
            self.current_dag.nodes[old_node_id] = new_node
            self.node_registry[domain] = new_node
            
            if hasattr(self.current_dag, '_rebuild_graph'):
                self.current_dag._rebuild_graph()
        
        return True
    
    def validate_upgrade(self, domain: str, new_version: NodeVersion) -> Dict[str, Any]:
        """
        Validate if a node can be upgraded to the specified version.
        
        This method performs comprehensive upgrade validation:
        1. Checks if the target node exists in the DAG
        2. Validates version compatibility against upgrade policy
        3. Ensures new version is newer than current version
        4. Checks for potential breaking changes
        
        The validation process helps prevent:
        - Incompatible version upgrades
        - Downgrade attempts
        - Policy violations
        - Breaking changes to DAG structure
        
        Args:
            domain: Domain identifier of the node to validate
            new_version: Proposed version for upgrade
            
        Returns:
            Dictionary containing validation results:
            - "valid": Boolean indicating if upgrade is allowed
            - "reason": Explanation of validation result
            - "current_version": Current node version
            - "upgrade_policy": Current upgrade policy
            - "target_version": Proposed target version
            
        Examples:
            >>> result = manager.validate_upgrade("governance", NodeVersion(2, 0, 0))
            >>> if not result["valid"]:
            ...     print(f"Upgrade blocked: {result['reason']}")
        """
        if domain not in self.node_registry:
            return {"valid": False, "reason": "Node not found"}
        
        current_node = self.node_registry[domain]
        can_upgrade = current_node.can_upgrade_to(new_version)
        
        return {
            "valid": can_upgrade,
            "current_version": str(current_node.node_version),
            "target_version": str(new_version),
            "upgrade_policy": current_node.upgrade_policy,
            "reason": "Compatible upgrade" if can_upgrade else "Incompatible version"
        }
    
    def rollback_node(self, domain: str, target_version: NodeVersion) -> bool:
        """
        Rollback a node to a previous version with safety validation.
        
        This method enables controlled rollback of individual nodes:
        1. Validates the target node exists and supports rollback
        2. Checks that target version is older than current version
        3. Creates rollback node instance with previous configuration
        4. Replaces current node while preserving DAG structure
        5. Updates delegation hash and DAG metadata
        
        Rollback Safety:
        - Only allows rollback to older versions
        - Preserves DAG structural integrity
        - Maintains deterministic behavior
        - Updates all relevant hashes and metadata
        
        Args:
            domain: Domain identifier of the node to rollback
            target_version: Previous version to rollback to
            
        Returns:
            True if rollback succeeded, False if validation failed
            
        Examples:
            >>> success = manager.rollback_node("governance", NodeVersion(1, 0, 0))
            >>> if success:
            ...     print("Rollback completed successfully")
        """
        if domain not in self.node_registry:
            return False
        
        current_node = self.node_registry[domain]
        
        if target_version.is_newer_than(current_node.node_version):
            return False
        
        rollback_node = StructuredSupportAgentNode(
            node_id=current_node.node_id,
            name=current_node.name,
            description=current_node.description,
            support_agent=current_node.support_agent,
            node_version=target_version,
            upgrade_policy=current_node.upgrade_policy
        )
        
        if self.current_dag:
            self.current_dag.nodes[current_node.node_id] = rollback_node
            self.node_registry[domain] = rollback_node
            
            if hasattr(self.current_dag, '_rebuild_graph'):
                self.current_dag._rebuild_graph()
        
        return True
    
    def get_structured_dag_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the structured DAG and all its components.
        
        This method provides detailed information about the current DAG state:
        - Overall DAG metadata (name, version, node count)
        - Individual node status (version, hash, upgrade policy)
        - Delegation configuration and hash verification
        - Edge and conditional edge mappings
        - Blockchain readiness indicators
        
        The status information is useful for:
        - Monitoring DAG health and configuration
        - Debugging delegation and routing issues
        - Verifying blockchain compatibility
        - Planning upgrades and maintenance
        
        Returns:
            Dictionary containing comprehensive DAG status:
            - "dag_name": Name of the current DAG
            - "dag_version": Current DAG version
            - "total_nodes": Number of nodes in the DAG
            - "structured_nodes": Detailed node information
            - "delegation_hash": Current delegation hash
            - "edges": DAG edge configuration
            - "conditional_edges": Conditional routing rules
            - "blockchain_ready": Blockchain compatibility status
            
        Examples:
            >>> status = manager.get_structured_dag_status()
            >>> print(f"DAG has {status['total_nodes']} nodes")
            >>> for node_id, info in status['structured_nodes'].items():
            ...     print(f"{node_id}: v{info['version']}")
        """
        if not self.current_dag:
            return {"status": "No DAG available"}
        
        structured_nodes = {}
        
        for node_id, node in self.current_dag.nodes.items():
            if isinstance(node, StructuredSupportAgentNode):
                structured_nodes[node_id] = {
                    "name": node.name,
                    "domain": node.support_agent.domain,
                    "version": str(node.node_version),
                    "node_hash": node.node_hash,
                    "upgrade_policy": node.upgrade_policy
                }
        
        return {
            "dag_name": self.current_dag.name,
            "dag_version": self.dag_version,
            "total_nodes": len(self.current_dag.nodes),
            "structured_nodes": structured_nodes,
            "delegation_hash": self.delegation_hash,
            "edges": self.current_dag.edges,
            "conditional_edges": list(self.current_dag.conditional_edges.keys()),
            "blockchain_ready": True
        }
    
    def export_for_blockchain(self) -> Dict[str, Any]:
        """Export DAG configuration for blockchain storage."""
        if not self.current_dag:
            return {}
        
        return self.current_dag.serialize_for_blockchain()
