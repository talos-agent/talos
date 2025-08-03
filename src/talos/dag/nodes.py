from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict, TYPE_CHECKING

from langchain_core.tools import BaseTool
from langchain_core.messages import BaseMessage
from langgraph.prebuilt import ToolNode as LangGraphToolNode
from pydantic import BaseModel, ConfigDict

from talos.core.agent import Agent
from talos.data.dataset_manager import DatasetManager
from talos.prompts.prompt_manager import PromptManager
from talos.services.abstract.service import Service
from talos.skills.base import Skill

if TYPE_CHECKING:
    from talos.prompts.prompt_config import PromptConfig
else:
    PromptConfig = "PromptConfig"


class GraphState(TypedDict):
    """State that flows through the DAG nodes."""
    messages: List[BaseMessage]
    context: Dict[str, Any]
    current_query: str
    results: Dict[str, Any]
    metadata: Dict[str, Any]


class DAGNode(BaseModel, ABC):
    """Abstract base class for all DAG nodes."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    node_id: str
    node_type: str
    name: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    @abstractmethod
    def execute(self, state: GraphState) -> GraphState:
        """Execute the node's functionality and return updated state."""
        pass
    
    @abstractmethod
    def get_node_config(self) -> Dict[str, Any]:
        """Return configuration for serialization."""
        pass


class AgentNode(DAGNode):
    """Node that wraps an Agent for execution in the DAG."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    agent: Agent
    node_type: str = "agent"
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute the agent with the current query."""
        query = state["current_query"]
        result = self.agent.run(query)
        
        state["results"][self.node_id] = result
        from langchain_core.messages import AIMessage
        state["messages"].append(AIMessage(content=f"Agent {self.name} processed: {query}"))
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "agent_type": type(self.agent).__name__,
            "metadata": self.metadata
        }


class SkillNode(DAGNode):
    """Node that wraps a Skill for execution in the DAG."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    skill: Skill
    node_type: str = "skill"
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute the skill with parameters from state."""
        context = state.get("context", {})
        result = self.skill.run(**context)
        
        state["results"][self.node_id] = result
        from langchain_core.messages import AIMessage
        state["messages"].append(AIMessage(content=f"Skill {self.name} executed"))
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "skill_name": self.skill.name,
            "metadata": self.metadata
        }


class ServiceNode(DAGNode):
    """Node that wraps a Service for execution in the DAG."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    service: Service
    node_type: str = "service"
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute the service with parameters from state."""
        state["results"][self.node_id] = f"Service {self.service.name} executed"
        from langchain_core.messages import AIMessage
        state["messages"].append(AIMessage(content=f"Service {self.name} processed"))
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "service_name": self.service.name,
            "metadata": self.metadata
        }


class ToolNode(DAGNode):
    """Node that wraps LangGraph's ToolNode for execution in the DAG."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    tools: List[BaseTool]
    node_type: str = "tool"
    _langgraph_tool_node: Optional[LangGraphToolNode] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.tools:
            self._langgraph_tool_node = LangGraphToolNode(self.tools)
    
    def execute(self, state: GraphState) -> GraphState:
        """Execute the tools using LangGraph's ToolNode."""
        if not self._langgraph_tool_node:
            state["results"][self.node_id] = "Error: No tools configured"
            return state
        
        try:
            result = self._langgraph_tool_node.invoke(state)
            state.update(result)
            state["results"][self.node_id] = "Tools executed successfully"
        except Exception as e:
            state["results"][self.node_id] = f"Error: {str(e)}"
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "tool_count": len(self.tools) if self.tools else 0
        }


class DataSourceNode(DAGNode):
    """Node that provides data from various sources."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    data_source: Any
    node_type: str = "data_source"
    
    def execute(self, state: GraphState) -> GraphState:
        """Retrieve data from the data source."""
        query = state["current_query"]
        
        if isinstance(self.data_source, DatasetManager):
            result = self.data_source.search(query, k=5)
            state["results"][self.node_id] = result
            state["context"]["relevant_documents"] = result
        else:
            state["results"][self.node_id] = f"Data from {self.name}"
        
        from langchain_core.messages import AIMessage
        state["messages"].append(AIMessage(content=f"Data source {self.name} provided data"))
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "data_source_type": type(self.data_source).__name__,
            "metadata": self.metadata
        }


class PromptNode(DAGNode):
    """Node that manages prompts and prompt templates."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    prompt_manager: PromptManager
    prompt_names: Optional[List[str]] = None
    prompt_config: Optional[PromptConfig] = None
    node_type: str = "prompt"
    
    def __init__(self, **data):
        if not data.get('prompt_names') and not data.get('prompt_config'):
            raise ValueError("Either prompt_names or prompt_config must be provided")
        super().__init__(**data)
        
    @classmethod
    def model_rebuild(cls):
        """Rebuild the model to resolve forward references."""
        super().model_rebuild()
    
    def execute(self, state: GraphState) -> GraphState:
        """Apply prompt templates to the current context."""
        if self.prompt_config:
            prompt = self.prompt_manager.get_prompt_with_config(
                self.prompt_config, 
                state.get("context", {})
            )
            config_desc = "declarative config"
        else:
            prompt = self.prompt_manager.get_prompt(self.prompt_names or [])
            config_desc = f"prompt names: {', '.join(self.prompt_names or [])}"
        
        if prompt:
            state["context"]["active_prompt"] = prompt.template
            state["results"][self.node_id] = f"Applied prompt using {config_desc}"
        else:
            state["results"][self.node_id] = f"Failed to load prompt using {config_desc}"
        
        from langchain_core.messages import AIMessage
        state["messages"].append(AIMessage(content=f"Prompt node {self.name} processed"))
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        config = {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "metadata": self.metadata
        }
        
        if self.prompt_config:
            config["prompt_config"] = "declarative"
        else:
            config["prompt_names"] = ", ".join(self.prompt_names) if self.prompt_names else None
            
        return config


class RouterNode(DAGNode):
    """Node that routes execution to different paths based on conditions."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    routing_logic: Dict[str, str]
    node_type: str = "router"
    
    def execute(self, state: GraphState) -> GraphState:
        """Determine the next node based on routing logic."""
        query = state["current_query"].lower()
        
        next_node = None
        for keyword, target_node in self.routing_logic.items():
            if keyword in query:
                next_node = target_node
                break
        
        state["context"]["next_node"] = next_node or "default"
        state["results"][self.node_id] = f"Routed to: {next_node or 'default'}"
        from langchain_core.messages import AIMessage
        state["messages"].append(AIMessage(content=f"Router {self.name} determined next path"))
        
        return state
    
    def get_node_config(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "name": self.name,
            "description": self.description,
            "routing_logic": self.routing_logic,
            "metadata": self.metadata
        }
