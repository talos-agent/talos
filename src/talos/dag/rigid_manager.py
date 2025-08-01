from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from pydantic import ConfigDict

from talos.dag.graph import TalosDAG
from talos.dag.manager import DAGManager
from talos.dag.nodes import PromptNode, DataSourceNode, ToolNode
from talos.dag.rigid_nodes import RigidSupportAgentNode, RigidRouterNode, NodeVersion
from talos.data.dataset_manager import DatasetManager
from talos.prompts.prompt_manager import PromptManager
from talos.services.abstract.service import Service
from talos.tools.tool_manager import ToolManager

pass


class RigidDAGManager(DAGManager):
    """
    Rigid DAG manager with controlled node upgrades for blockchain-native AI.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    node_registry: Dict[str, RigidSupportAgentNode] = {}
    delegation_hash: str = ""
    dag_version: str = "1.0.0"
    
    def create_rigid_dag(
        self,
        model: BaseChatModel,
        prompt_manager: PromptManager,
        support_agents: Dict[str, Any],
        services: List[Service],
        tool_manager: ToolManager,
        dataset_manager: Optional[DatasetManager] = None,
        dag_name: str = "rigid_talos_dag"
    ) -> TalosDAG:
        """Create a rigid DAG with deterministic structure."""
        
        dag = TalosDAG(
            name=dag_name,
            description="Rigid Talos agent DAG with blockchain-native node upgrades"
        )
        
        delegation_rules = self._create_deterministic_delegation(support_agents)
        self.delegation_hash = self._calculate_delegation_hash(delegation_rules)
        
        prompt_node = PromptNode(
            node_id="main_prompt",
            name="Main Agent Prompt",
            description="Primary prompt for the rigid Talos agent",
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
        
        router_node = RigidRouterNode(
            node_id="rigid_router",
            name="Rigid Router",
            description="Deterministic router with hash-based delegation",
            delegation_rules=delegation_rules
        )
        dag.add_node(router_node)
        
        if dataset_manager:
            dag.add_edge("dataset_source", "rigid_router")
        else:
            dag.add_edge("main_prompt", "rigid_router")
        
        for domain, agent in support_agents.items():
            rigid_node = RigidSupportAgentNode(
                node_id=f"{domain}_agent",
                name=f"{domain.title()} Agent",
                description=agent.description,
                support_agent=agent,
                node_version=NodeVersion(major=1, minor=0, patch=0)
            )
            dag.add_node(rigid_node)
            self.node_registry[domain] = rigid_node
        
        if tool_manager.tools:
            tools_list = list(tool_manager.tools.values())
            tool_node = ToolNode(
                node_id="rigid_tools",
                name="Rigid Tools",
                description="LangGraph tools for rigid operations",
                tools=tools_list
            )
            dag.add_node(tool_node)
        
        conditional_targets = {}
        for keyword, target in delegation_rules.items():
            if target in [node.node_id for node in dag.nodes.values()]:
                conditional_targets[target] = target
        
        if conditional_targets:
            dag.add_conditional_edge("rigid_router", conditional_targets)
        
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
        Upgrade a specific support agent node with version compatibility checks.
        """
        if not self.current_dag or domain not in self.node_registry:
            return False
        
        current_node = self.node_registry[domain]
        
        if not force and not current_node.can_upgrade_to(new_version):
            return False
        
        old_node_id = current_node.node_id
        
        new_node = RigidSupportAgentNode(
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
        """Validate if a node upgrade is possible."""
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
        """Rollback a node to a previous version."""
        if domain not in self.node_registry:
            return False
        
        current_node = self.node_registry[domain]
        
        if target_version.is_newer_than(current_node.node_version):
            return False
        
        rollback_node = RigidSupportAgentNode(
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
    
    def get_rigid_dag_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the rigid DAG."""
        if not self.current_dag:
            return {"status": "No DAG available"}
        
        rigid_nodes = {}
        
        for node_id, node in self.current_dag.nodes.items():
            if isinstance(node, RigidSupportAgentNode):
                rigid_nodes[node_id] = {
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
            "rigid_nodes": rigid_nodes,
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
