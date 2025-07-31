from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict

from talos.dag.graph import TalosDAG
from talos.dag.nodes import (
    SkillNode, ServiceNode, ToolNode, 
    DataSourceNode, PromptNode, RouterNode, GraphState
)
from talos.data.dataset_manager import DatasetManager
from talos.prompts.prompt_manager import PromptManager
from talos.services.abstract.service import Service
from talos.skills.base import Skill
from talos.tools.tool_manager import ToolManager


class DAGManager(BaseModel):
    """Manages DAG creation, modification, and execution."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    current_dag: Optional[TalosDAG] = None
    dag_history: List[TalosDAG] = []
    
    def create_default_dag(
        self,
        model: BaseChatModel,
        prompt_manager: PromptManager,
        skills: List[Skill],
        services: List[Service],
        tool_manager: ToolManager,
        dataset_manager: Optional[DatasetManager] = None
    ) -> TalosDAG:
        """Create a default DAG from existing Talos components."""
        dag = TalosDAG(
            name="talos_default_dag",
            description="Default Talos agent DAG with integrated skills, services, and tools"
        )
        
        prompt_node = PromptNode(
            node_id="main_prompt",
            name="Main Agent Prompt",
            description="Primary prompt for the Talos agent",
            prompt_manager=prompt_manager,
            prompt_names=["main_agent_prompt", "general_agent_prompt"]
        )
        dag.add_node(prompt_node)
        
        routing_logic = {
            "proposal": "proposals_skill",
            "twitter": "twitter_sentiment_skill", 
            "github": "pr_review_skill",
            "crypto": "cryptography_skill",
            "sentiment": "twitter_sentiment_skill",
            "review": "pr_review_skill"
        }
        router_node = RouterNode(
            node_id="main_router",
            name="Main Router",
            description="Routes queries to appropriate skills",
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
            dag.add_edge("dataset_source", "main_router")
        else:
            dag.add_edge("main_prompt", "main_router")
        
        for skill in skills:
            skill_node = SkillNode(
                node_id=f"{skill.name}_skill",
                name=f"{skill.name.title()} Skill",
                description=f"Skill for {skill.name} operations",
                skill=skill
            )
            dag.add_node(skill_node)
        
        for service in services:
            service_node = ServiceNode(
                node_id=f"{service.name}_service",
                name=f"{service.name.title()} Service",
                description=f"Service for {service.name} operations",
                service=service
            )
            dag.add_node(service_node)
        
        if tool_manager.tools:
            tools_list = list(tool_manager.tools.values())
            tool_node = ToolNode(
                node_id="tools",
                name="Tools",
                description="LangGraph tools for various operations",
                tools=tools_list
            )
            dag.add_node(tool_node)
        
        conditional_targets = {}
        for keyword, target in routing_logic.items():
            if target in [node.node_id for node in dag.nodes.values()]:
                conditional_targets[target] = target
        
        if conditional_targets:
            dag.add_conditional_edge("main_router", conditional_targets)
        
        self.current_dag = dag
        return dag
    
    def execute_dag(self, query: str, context: Optional[Dict[str, Any]] = None, thread_id: str = "default") -> GraphState:
        """Execute the current DAG with a query."""
        if not self.current_dag:
            raise ValueError("No DAG available for execution")
        
        initial_state: GraphState = {
            "messages": [],
            "context": context or {},
            "current_query": query,
            "results": {},
            "metadata": {"dag_name": self.current_dag.name}
        }
        
        return self.current_dag.execute(initial_state, thread_id=thread_id)
    
    def get_dag_visualization(self) -> str:
        """Get a text visualization of the current DAG."""
        if not self.current_dag:
            return "No DAG available"
        
        return self.current_dag.visualize_graph()
    
    def serialize_dag_for_chain(self) -> str:
        """Serialize the current DAG for on-chain storage."""
        if not self.current_dag:
            return "{}"
        
        return self.current_dag.serialize_to_json()
    
    def rollback_to_previous_dag(self) -> bool:
        """Rollback to the previous DAG version."""
        if not self.dag_history:
            return False
        
        self.current_dag = self.dag_history.pop()
        return True
