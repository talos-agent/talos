from __future__ import annotations

from typing import Any, Dict, List, Optional

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
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        if self.dag_manager is None:
            self.dag_manager = DAGManager()
    
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
            
        self.dag_manager.create_default_dag(
            model=self.model,
            prompt_manager=self.prompt_manager,
            skills=skills,
            services=services,
            tool_manager=tool_manager,
            dataset_manager=dataset_manager
        )
    
    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:
        """Execute the query using the DAG instead of traditional agent flow."""
        if self.memory:
            relevant_memories = self.memory.search(message)
            kwargs["relevant_memories"] = relevant_memories
            
            if history is None:
                history = self.memory.load_history()
        
        context = self._build_context(message, **kwargs)
        context.update(kwargs)
        
        if history:
            context["conversation_history"] = [msg.content for msg in history]
        
        try:
            if self.dag_manager is None:
                raise ValueError("DAG manager not initialized")
            result_state = self.dag_manager.execute_dag(message, context)
            
            processed_result = self._process_dag_result(result_state, message)
            
            if self.memory:
                from langchain_core.messages import AIMessage
                if isinstance(processed_result, AIMessage):
                    self.add_to_history([processed_result])
                    self.memory.save_history(self.history)
            
            return processed_result
            
        except Exception as e:
            if self.verbose:
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
    
    def propose_dag_modification(
        self,
        title: str,
        description: str,
        proposed_changes: Dict[str, Any],
        rationale: str
    ) -> str:
        """Propose a modification to the DAG architecture."""
        if self.dag_manager is None:
            raise ValueError("DAG manager not initialized")
        proposal = self.dag_manager.propose_dag_modification(
            title=title,
            description=description,
            proposed_changes=proposed_changes,
            rationale=rationale
        )
        return proposal.proposal_id
    
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
    
    def evaluate_dag_proposal(self, proposal_id: str, approved: bool) -> bool:
        """Evaluate and potentially apply a DAG modification proposal."""
        if self.dag_manager is None:
            return False
        return self.dag_manager.evaluate_proposal(proposal_id, approved)
    
    def get_proposal_status(self) -> Dict[str, Any]:
        """Get the status of all DAG modification proposals."""
        if self.dag_manager is None:
            return {"pending": 0, "approved": 0, "pending_proposals": [], "approved_proposals": []}
        return self.dag_manager.get_proposal_status()
