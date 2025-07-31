from __future__ import annotations

from typing import Any

from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel, ConfigDict

from talos.dag.dag_agent import DAGAgent
from talos.prompts.prompt_manager import PromptManager
from talos.skills.base import Skill


class DAGProposalResult(BaseModel):
    """Result of DAG proposal evaluation."""
    proposal_id: str
    title: str
    description: str
    evaluation: str
    recommendation: str
    approved: bool


class DAGProposalSkill(Skill):
    """Skill for evaluating and managing DAG architecture proposals."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    llm: BaseChatModel
    prompt_manager: PromptManager
    dag_agent: DAGAgent
    
    @property
    def name(self) -> str:
        return "dag_proposal"
    
    def run(self, **kwargs: Any) -> DAGProposalResult:
        """Evaluate a DAG modification proposal."""
        proposal_title = kwargs.get("title", "")
        proposal_description = kwargs.get("description", "")
        proposed_changes = kwargs.get("proposed_changes", {})
        rationale = kwargs.get("rationale", "")
        
        proposal_id = self.dag_agent.propose_dag_modification(
            title=proposal_title,
            description=proposal_description,
            proposed_changes=proposed_changes,
            rationale=rationale
        )
        
        current_dag_viz = self.dag_agent.get_dag_visualization()
        
        evaluation_prompt = f"""
        You are evaluating a proposal to modify the Talos agent DAG architecture.
        
        Current DAG Structure:
        {current_dag_viz}
        
        Proposal Details:
        Title: {proposal_title}
        Description: {proposal_description}
        Rationale: {rationale}
        Proposed Changes: {proposed_changes}
        
        Please evaluate this proposal considering:
        1. Technical feasibility
        2. Impact on existing functionality
        3. Security implications
        4. Performance considerations
        5. Alignment with Talos agent goals
        
        Provide your evaluation and recommendation (approve/reject) with reasoning.
        """
        
        evaluation_result = self.llm.invoke(evaluation_prompt)
        if hasattr(evaluation_result, 'content'):
            evaluation_text = str(evaluation_result.content)
        else:
            evaluation_text = str(evaluation_result)
        
        approved = "approve" in evaluation_text.lower() and "reject" not in evaluation_text.lower()
        
        if approved:
            self.dag_agent.evaluate_dag_proposal(proposal_id, True)
            recommendation = "APPROVED - Proposal has been applied to the DAG"
        else:
            recommendation = "REJECTED - Proposal does not meet evaluation criteria"
        
        return DAGProposalResult(
            proposal_id=proposal_id,
            title=proposal_title,
            description=proposal_description,
            evaluation=evaluation_text,
            recommendation=recommendation,
            approved=approved
        )
