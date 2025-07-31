from __future__ import annotations

from typing import Any, Dict, Optional, TYPE_CHECKING

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage
from pydantic import ConfigDict

from talos.dag.nodes import DAGNode, GraphState

if TYPE_CHECKING:
    from talos.core.extensible_agent import SkillAgent


class ExtensibleSkillNode(DAGNode):
    """
    Enhanced skill node that supports individual configurations and chat capabilities.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    skill_agent: "SkillAgent"
    node_type: str = "extensible_skill"
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute the skill agent with enhanced capabilities."""
        query = state["current_query"]
        context = state.get("context", {})
        
        enhanced_context = self.skill_agent.gather_information(query, context)
        
        enhanced_context.update({
            "current_query": query,
            "messages": state.get("messages", []),
            "results": state.get("results", {}),
            "metadata": state.get("metadata", {})
        })
        
        result = self.skill_agent.execute_with_context(enhanced_context)
        
        state["results"][self.node_id] = result
        state["messages"].append(
            AIMessage(content=f"Extensible skill {self.name} executed: {str(result)[:100]}...")
        )
        
        state["metadata"][f"{self.node_id}_config"] = {
            "individual_memory": self.skill_agent.use_individual_memory,
            "chat_enabled": self.skill_agent.chat_enabled,
            "skill_type": type(self.skill_agent.skill).__name__
        }
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        """Return enhanced configuration for serialization."""
        base_config = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "skill_name": self.skill_agent.name,
            "metadata": self.metadata
        }
        
        base_config["skill_agent_config"] = {
            "individual_memory": self.skill_agent.use_individual_memory,
            "shared_memory": self.skill_agent.use_shared_memory,
            "chat_enabled": self.skill_agent.chat_enabled,
            "has_individual_model": self.skill_agent.model is not None,
            "skill_description": self.skill_agent.description
        }
        
        return base_config


class ConfigurableAgentNode(DAGNode):
    """
    Agent node that can be configured with different models and settings.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    agent_config: Dict[str, Any]
    model: Optional[BaseChatModel] = None
    node_type: str = "configurable_agent"
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute with configurable agent settings."""
        query = state["current_query"]
        
        model = self.model
        if not model:
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model="gpt-4o-mini")
        
        try:
            from langchain_core.messages import HumanMessage
            response = model.invoke([HumanMessage(content=f"Process this query: {query}")])
            result = response.content
        except Exception as e:
            result = f"Error in configurable agent: {str(e)}"
        
        state["results"][self.node_id] = result
        state["messages"].append(
            AIMessage(content=f"Configurable agent {self.name} processed: {query}")
        )
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "agent_config": self.agent_config,
            "has_individual_model": self.model is not None,
            "metadata": self.metadata
        }
