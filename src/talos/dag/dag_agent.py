from __future__ import annotations

from typing import Any, List, Optional, Union

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict

from talos.core.agent import Agent
from talos.dag.manager import DAGManager
from talos.dag.nodes import GraphState
from talos.data.dataset_manager import DatasetManager
from talos.services.abstract.service import Service
from talos.skills.base import Skill
from talos.tools.tool_manager import ToolManager


class DAGAgent(Agent):
    """Agent that uses DAG-based execution instead of traditional linear flow."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    dag_manager: Optional[DAGManager] = None
    verbose: Union[bool, int] = False
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if self.dag_manager is None:
            self.dag_manager = DAGManager()
    
    def _get_verbose_level(self) -> int:
        """Convert verbose to integer level for backward compatibility."""
        if isinstance(self.verbose, bool):
            return 1 if self.verbose else 0
        return max(0, min(2, self.verbose))
    
    def setup_dag(
        self,
        skills: List[Skill],
        services: List[Service],
        tool_manager: ToolManager,
        dataset_manager: Optional[DatasetManager] = None
    ) -> None:
        """Set up the DAG with the provided components."""
        if not self.prompt_manager:
            raise ValueError("Prompt manager must be initialized before setting up DAG")
        
        if self.dag_manager is None:
            self.dag_manager = DAGManager()
            
        from langchain_core.language_models import BaseChatModel
        if not isinstance(self.model, BaseChatModel):
            raise ValueError("DAG requires a BaseChatModel, got: " + str(type(self.model)))
        
        if dataset_manager and self.user_id and not dataset_manager.use_database:
            if self.verbose:
                print("🔄 Upgrading DatasetManager to use database persistence")
            
            from talos.database.session import init_database
            from langchain_openai import OpenAIEmbeddings
            
            init_database()
            
            dataset_manager = DatasetManager(
                verbose=dataset_manager.verbose,
                user_id=self.user_id,
                session_id=self.session_id or "dag-session",
                use_database=True,
                embeddings=OpenAIEmbeddings()
            )
            
        self.dag_manager.create_default_dag(
            model=self.model,
            prompt_manager=self.prompt_manager,
            skills=skills,
            services=services,
            tool_manager=tool_manager,
            dataset_manager=dataset_manager
        )
    
    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:
        """Execute the query using the DAG with LangGraph memory patterns."""
        thread_id = kwargs.get("thread_id", "default_conversation")
        
        context = self._build_context(message, **kwargs)
        context.update(kwargs)
        
        try:
            if self.dag_manager is None:
                raise ValueError("DAG manager not initialized")
            result_state = self.dag_manager.execute_dag(message, context, thread_id=thread_id)
            
            processed_result = self._process_dag_result(result_state, message)
            return processed_result
            
        except Exception as e:
            if self._get_verbose_level() >= 1:
                print(f"DAG execution failed, falling back to traditional agent: {e}")
            return super().run(message, history, **kwargs)
    
    def _process_dag_result(self, result_state: GraphState, original_query: str) -> BaseModel:
        """Process the DAG execution result into a standard agent response."""
        from langchain_core.messages import AIMessage
        
        results = result_state.get("results", {})
        messages = result_state.get("messages", [])
        
        response_parts = []
        
        if results:
            response_parts.append("DAG Execution Results:")
            for node_id, result in results.items():
                response_parts.append(f"- {node_id}: {str(result)[:200]}...")
        
        if messages:
            response_parts.append("\nExecution Flow:")
            response_parts.extend(f"- {msg}" for msg in messages[-5:])  # Last 5 messages
        
        response_content = "\n".join(response_parts) if response_parts else "DAG execution completed"
        
        ai_message = AIMessage(content=response_content)
        self.history.append(ai_message)
        
        return ai_message
    
    def get_dag_visualization(self) -> str:
        """Get a visualization of the current DAG structure."""
        if self.dag_manager is None:
            return "DAG manager not initialized"
        return self.dag_manager.get_dag_visualization()
    
    def get_dag_config_for_chain(self) -> str:
        """Get the DAG configuration serialized for on-chain storage."""
        if self.dag_manager is None:
            return "{}"
        return self.dag_manager.serialize_dag_for_chain()
