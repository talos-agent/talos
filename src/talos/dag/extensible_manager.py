from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from langchain_core.language_models import BaseChatModel
from pydantic import ConfigDict

from talos.dag.extensible_nodes import ExtensibleSkillNode, ConfigurableAgentNode

if TYPE_CHECKING:
    from talos.core.extensible_agent import SupportAgent, SupportAgentRegistry
from talos.dag.graph import TalosDAG
from talos.dag.manager import DAGManager
from talos.dag.nodes import (
    DataSourceNode, PromptNode, RouterNode, ToolNode
)
from talos.data.dataset_manager import DatasetManager
from talos.prompts.prompt_manager import PromptManager
from talos.services.abstract.service import Service
from talos.tools.tool_manager import ToolManager


class ExtensibleDAGManager(DAGManager):
    """
    Enhanced DAG manager that supports extensible skill agents and dynamic reconfiguration.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    skill_registry: Optional["SupportAgentRegistry"] = None
    
    def create_extensible_dag(
        self,
        model: BaseChatModel,
        prompt_manager: PromptManager,
        skill_registry: "SupportAgentRegistry",
        services: List[Service],
        tool_manager: ToolManager,
        dataset_manager: Optional[DatasetManager] = None,
        dag_name: str = "extensible_talos_dag"
    ) -> TalosDAG:
        """Create a DAG with extensible skill agents."""
        self.skill_registry = skill_registry
        
        dag = TalosDAG(
            name=dag_name,
            description="Extensible Talos agent DAG with configurable skill agents"
        )
        
        from talos.prompts.prompt_config import PromptConfig, StaticPromptSelector
        
        legacy_config = PromptConfig(
            selector=StaticPromptSelector(
                prompt_names=["main_agent_prompt", "general_agent_prompt"]
            )
        )
        
        prompt_node = PromptNode(
            node_id="main_prompt",
            name="Main Agent Prompt",
            description="Primary prompt for the extensible Talos agent",
            prompt_manager=prompt_manager,
            prompt_config=legacy_config
        )
        dag.add_node(prompt_node)
        
        routing_logic = {}
        skill_agents = skill_registry.get_all_agents()
        
        for skill_name, skill_agent in skill_agents.items():
            routing_logic[skill_name.lower()] = f"{skill_name}_skill"
            
            if "proposal" in skill_name.lower():
                routing_logic["proposal"] = f"{skill_name}_skill"
                routing_logic["governance"] = f"{skill_name}_skill"
            elif "twitter" in skill_name.lower():
                routing_logic["twitter"] = f"{skill_name}_skill"
                routing_logic["sentiment"] = f"{skill_name}_skill"
            elif "github" in skill_name.lower() or "pr" in skill_name.lower():
                routing_logic["github"] = f"{skill_name}_skill"
                routing_logic["review"] = f"{skill_name}_skill"
            elif "crypto" in skill_name.lower():
                routing_logic["crypto"] = f"{skill_name}_skill"
                routing_logic["encrypt"] = f"{skill_name}_skill"
        
        router_node = RouterNode(
            node_id="extensible_router",
            name="Extensible Router",
            description="Routes queries to appropriate extensible skill agents",
            routing_logic=routing_logic
        )
        dag.add_node(router_node)
        
        if dataset_manager:
            data_node = DataSourceNode(
                node_id="dataset_source",
                name="Dataset Manager",
                description="Provides relevant documents and context",
                data_source=dataset_manager
            )
            dag.add_node(data_node)
            dag.add_edge("main_prompt", "dataset_source")
            dag.add_edge("dataset_source", "extensible_router")
        else:
            dag.add_edge("main_prompt", "extensible_router")
        
        for skill_name, skill_agent in skill_agents.items():
            skill_node = ExtensibleSkillNode(
                node_id=f"{skill_name}_skill",
                name=f"{skill_name.title()} Skill",
                description=skill_agent.description or f"Extensible skill for {skill_name} operations",
                skill_agent=skill_agent
            )
            dag.add_node(skill_node)
        
        for service in services:
            service_node = ConfigurableAgentNode(
                node_id=f"{service.name}_service",
                name=f"{service.name.title()} Service",
                description=f"Configurable service for {service.name} operations",
                agent_config={"service_type": type(service).__name__},
                model=model
            )
            dag.add_node(service_node)
        
        if tool_manager.tools:
            tools_list = list(tool_manager.tools.values())
            tool_node = ToolNode(
                node_id="extensible_tools",
                name="Extensible Tools",
                description="LangGraph tools for various operations",
                tools=tools_list
            )
            dag.add_node(tool_node)
        
        conditional_targets = {}
        for keyword, target in routing_logic.items():
            if target in [node.node_id for node in dag.nodes.values()]:
                conditional_targets[target] = target
        
        if conditional_targets:
            dag.add_conditional_edge("extensible_router", conditional_targets)
        
        self.current_dag = dag
        return dag
    
    def add_skill_to_dag(self, skill_agent: "SupportAgent") -> bool:
        """Add a new skill agent to the current DAG."""
        if not self.current_dag or not self.skill_registry:
            return False
        
        self.skill_registry.register_agent(skill_agent)
        
        skill_node = ExtensibleSkillNode(
            node_id=f"{skill_agent.name}_skill",
            name=f"{skill_agent.name.title()} Skill",
            description=skill_agent.description or f"Extensible skill for {skill_agent.name} operations",
            skill_agent=skill_agent
        )
        self.current_dag.add_node(skill_node)
        
        router_node = self.current_dag.nodes.get("extensible_router")
        if router_node and hasattr(router_node, 'routing_logic'):
            router_node.routing_logic[skill_agent.name.lower()] = f"{skill_agent.name}_skill"
            
            conditional_targets = {}
            for keyword, target in router_node.routing_logic.items():
                if target in [node.node_id for node in self.current_dag.nodes.values()]:
                    conditional_targets[target] = target
            
            if conditional_targets:
                self.current_dag.conditional_edges["extensible_router"] = conditional_targets
                self.current_dag._rebuild_graph()
        
        return True
    
    def remove_skill_from_dag(self, skill_name: str) -> bool:
        """Remove a skill agent from the current DAG."""
        if not self.current_dag or not self.skill_registry:
            return False
        
        success = self.skill_registry.unregister_agent(skill_name)
        if not success:
            return False
        
        node_id = f"{skill_name}_skill"
        success = self.current_dag.remove_node(node_id)
        
        router_node = self.current_dag.nodes.get("extensible_router")
        if router_node and hasattr(router_node, 'routing_logic'):
            keys_to_remove = [k for k, v in router_node.routing_logic.items() if v == node_id]
            for key in keys_to_remove:
                del router_node.routing_logic[key]
            
            conditional_targets = {}
            for keyword, target in router_node.routing_logic.items():
                if target in [node.node_id for node in self.current_dag.nodes.values()]:
                    conditional_targets[target] = target
            
            if conditional_targets:
                self.current_dag.conditional_edges["extensible_router"] = conditional_targets
            else:
                if "extensible_router" in self.current_dag.conditional_edges:
                    del self.current_dag.conditional_edges["extensible_router"]
            
            self.current_dag._rebuild_graph()
        
        return success
    
    def get_extensible_dag_status(self) -> Dict[str, Any]:
        """Get status of the extensible DAG."""
        if not self.current_dag:
            return {"status": "No DAG available"}
        
        skill_nodes = {}
        configurable_nodes = {}
        
        for node_id, node in self.current_dag.nodes.items():
            if isinstance(node, ExtensibleSkillNode):
                skill_nodes[node_id] = {
                    "name": node.name,
                    "skill_agent": node.skill_agent.name,
                    "domain": node.skill_agent.domain,
                    "architecture": node.skill_agent.architecture
                }
            elif isinstance(node, ConfigurableAgentNode):
                configurable_nodes[node_id] = {
                    "name": node.name,
                    "config": node.agent_config,
                    "has_individual_model": node.model is not None
                }
        
        return {
            "dag_name": self.current_dag.name,
            "total_nodes": len(self.current_dag.nodes),
            "skill_nodes": skill_nodes,
            "configurable_nodes": configurable_nodes,
            "edges": self.current_dag.edges,
            "conditional_edges": list(self.current_dag.conditional_edges.keys()),
            "registered_skills": self.skill_registry.list_agents() if self.skill_registry else []
        }
