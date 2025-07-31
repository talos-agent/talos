from __future__ import annotations

from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict

from talos.core.memory import Memory
from talos.dag.dag_agent import DAGAgent
from talos.dag.manager import DAGManager
from talos.data.dataset_manager import DatasetManager
from talos.prompts.prompt_manager import PromptManager
from talos.skills.base import Skill


class SkillAgent(BaseModel):
    """
    Individual skill agent with its own configuration, memory, and LLM.
    Can gather additional information via chat before executing actions.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    skill: Skill
    name: str
    description: Optional[str] = None
    
    model: Optional[BaseChatModel] = None
    memory: Optional[Memory] = None
    dataset_manager: Optional[DatasetManager] = None
    prompt_manager: Optional[PromptManager] = None
    
    use_individual_memory: bool = False
    use_shared_memory: bool = True
    chat_enabled: bool = True
    
    conversation_history: List[BaseMessage] = []
    
    def model_post_init(self, __context: Any) -> None:
        if self.use_individual_memory and not self.memory:
            self._setup_individual_memory()
    
    def _setup_individual_memory(self) -> None:
        """Setup individual memory for this skill agent."""
        from langchain_openai import OpenAIEmbeddings
        from pathlib import Path
        
        embeddings_model = OpenAIEmbeddings()
        memory_dir = Path("memory") / f"skill_{self.name}"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory = Memory(
            file_path=memory_dir / "memories.json",
            embeddings_model=embeddings_model,
            history_file_path=memory_dir / "history.json",
            use_database=False,
            auto_save=True,
            verbose=False,
        )
    
    def gather_information(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Gather additional information via chat before executing the skill.
        This allows the skill agent to ask clarifying questions or gather context.
        """
        if not self.chat_enabled:
            return context
        
        model = self.model
        if not model:
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model="gpt-4o-mini")
        
        info_gathering_prompt = f"""
        You are a specialized skill agent for: {self.name}
        Description: {self.description or 'No description provided'}
        
        You have been asked to handle this query: {query}
        Current context: {context}
        
        Determine if you need additional information to properly execute this skill.
        If you need more information, respond with a JSON object containing:
        {{
            "needs_info": true,
            "questions": ["question1", "question2", ...],
            "reasoning": "why you need this information"
        }}
        
        If you have enough information, respond with:
        {{
            "needs_info": false,
            "ready_to_execute": true
        }}
        """
        
        try:
            from langchain_core.messages import HumanMessage
            model.invoke([HumanMessage(content=info_gathering_prompt)])
            
            enhanced_context = context.copy()
            enhanced_context["skill_agent_processed"] = True
            enhanced_context["skill_name"] = self.name
            
            return enhanced_context
            
        except Exception:
            return context
    
    def execute_with_context(self, context: Dict[str, Any]) -> Any:
        """Execute the skill with the gathered context."""
        if self.memory and self.use_individual_memory:
            memory_context = self.memory.search(context.get("current_query", ""), k=3)
            context["individual_memory"] = memory_context
        
        result = self.skill.run(**context)
        
        if self.memory and self.use_individual_memory:
            self.memory.add_memory(
                f"Executed {self.name}: {str(result)[:200]}",
                {"skill": self.name, "context": context}
            )
        
        return result


class SkillRegistry(BaseModel):
    """Registry for managing skill agents dynamically."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _skills: Dict[str, SkillAgent] = {}
    
    def register_skill(self, skill_agent: SkillAgent) -> None:
        """Register a new skill agent."""
        self._skills[skill_agent.name] = skill_agent
    
    def unregister_skill(self, skill_name: str) -> bool:
        """Remove a skill agent."""
        if skill_name in self._skills:
            del self._skills[skill_name]
            return True
        return False
    
    def get_skill(self, skill_name: str) -> Optional[SkillAgent]:
        """Get a skill agent by name."""
        return self._skills.get(skill_name)
    
    def list_skills(self) -> List[str]:
        """List all registered skill names."""
        return list(self._skills.keys())
    
    def get_all_skills(self) -> Dict[str, SkillAgent]:
        """Get all registered skill agents."""
        return self._skills.copy()


class ExtensibleMainAgent(DAGAgent):
    """
    Main agent that provides an extensible framework for managing skill agents.
    Supports easy addition/removal of capabilities and individual skill configurations.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    skill_registry: SkillRegistry = SkillRegistry()
    interaction_mode: str = "orchestrated"  # "orchestrated" or "direct"
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_default_skills()
    
    def _setup_default_skills(self) -> None:
        """Setup default skills as skill agents."""
        from talos.skills.proposals import ProposalsSkill
        from talos.skills.cryptography import CryptographySkill
        
        if self.prompt_manager:
            proposals_skill_agent = SkillAgent(
                skill=ProposalsSkill(llm=self.model, prompt_manager=self.prompt_manager),  # type: ignore
                name="proposals",
                description="Evaluates governance proposals using AI analysis",
                use_individual_memory=True,
                chat_enabled=True
            )
            self.skill_registry.register_skill(proposals_skill_agent)
        
        crypto_skill_agent = SkillAgent(
            skill=CryptographySkill(),
            name="cryptography",
            description="Provides encryption and decryption capabilities",
            use_individual_memory=False,
            chat_enabled=False
        )
        
        self.skill_registry.register_skill(crypto_skill_agent)
        
        self._setup_optional_skills()
    
    def _setup_optional_skills(self) -> None:
        """Setup optional skills that depend on external services."""
        try:
            from talos.skills.twitter_sentiment import TwitterSentimentSkill
            from talos.tools.twitter_client import TwitterConfig
            
            TwitterConfig()  # Check if Twitter token is available
            
            if self.prompt_manager:
                twitter_skill_agent = SkillAgent(
                    skill=TwitterSentimentSkill(prompt_manager=self.prompt_manager),
                    name="twitter_sentiment",
                    description="Analyzes Twitter sentiment for queries",
                    use_individual_memory=True,
                    chat_enabled=True
                )
                self.skill_registry.register_skill(twitter_skill_agent)
            
        except (ImportError, ValueError):
            pass  # Twitter dependencies not available
        
        try:
            from talos.skills.pr_review import PRReviewSkill
            from talos.tools.github.tools import GithubTools
            from talos.settings import GitHubSettings
            
            github_settings = GitHubSettings()
            if github_settings.GITHUB_API_TOKEN and self.prompt_manager:
                pr_review_skill_agent = SkillAgent(
                    skill=PRReviewSkill(
                        llm=self.model,  # type: ignore
                        prompt_manager=self.prompt_manager,
                        github_tools=GithubTools(token=github_settings.GITHUB_API_TOKEN)
                    ),
                    name="pr_review",
                    description="Reviews GitHub pull requests and provides feedback",
                    use_individual_memory=True,
                    chat_enabled=True
                )
                self.skill_registry.register_skill(pr_review_skill_agent)
                
        except (ImportError, ValueError):
            pass  # GitHub dependencies not available
    
    def add_skill_agent(
        self,
        skill: Skill,
        name: str,
        description: Optional[str] = None,
        model: Optional[BaseChatModel] = None,
        use_individual_memory: bool = False,
        chat_enabled: bool = True,
        **kwargs
    ) -> SkillAgent:
        """
        Add a new skill agent to the system.
        
        Args:
            skill: The skill instance to wrap
            name: Unique name for the skill agent
            description: Description of the skill's capabilities
            model: Optional individual LLM for this skill
            use_individual_memory: Whether to use individual memory
            chat_enabled: Whether the skill can gather info via chat
            **kwargs: Additional configuration options
        
        Returns:
            The created SkillAgent instance
        """
        skill_agent = SkillAgent(
            skill=skill,
            name=name,
            description=description,
            model=model,
            use_individual_memory=use_individual_memory,
            chat_enabled=chat_enabled,
            **kwargs
        )
        
        self.skill_registry.register_skill(skill_agent)
        self._rebuild_dag()
        
        return skill_agent
    
    def remove_skill_agent(self, skill_name: str) -> bool:
        """
        Remove a skill agent from the system.
        
        Args:
            skill_name: Name of the skill to remove
            
        Returns:
            True if skill was removed, False if not found
        """
        success = self.skill_registry.unregister_skill(skill_name)
        if success:
            self._rebuild_dag()
        return success
    
    def list_skill_agents(self) -> List[str]:
        """List all available skill agents."""
        return self.skill_registry.list_skills()
    
    def get_skill_agent(self, skill_name: str) -> Optional[SkillAgent]:
        """Get a specific skill agent by name."""
        return self.skill_registry.get_skill(skill_name)
    
    def set_interaction_mode(self, mode: str) -> None:
        """
        Set the interaction mode.
        
        Args:
            mode: "orchestrated" for main agent coordination, "direct" for direct skill access
        """
        if mode not in ["orchestrated", "direct"]:
            raise ValueError("Mode must be 'orchestrated' or 'direct'")
        self.interaction_mode = mode
    
    def interact_with_skill(self, skill_name: str, query: str, **kwargs) -> Any:
        """
        Directly interact with a specific skill agent.
        
        Args:
            skill_name: Name of the skill to interact with
            query: Query to send to the skill
            **kwargs: Additional context for the skill
            
        Returns:
            Result from the skill execution
        """
        skill_agent = self.skill_registry.get_skill(skill_name)
        if not skill_agent:
            raise ValueError(f"Skill '{skill_name}' not found")
        
        context = {"current_query": query, **kwargs}
        enhanced_context = skill_agent.gather_information(query, context)
        
        return skill_agent.execute_with_context(enhanced_context)
    
    def _rebuild_dag(self) -> None:
        """Rebuild the DAG with current skill agents."""
        if not self.dag_manager:
            self.dag_manager = DAGManager()
        
        skills = [skill_agent.skill for skill_agent in self.skill_registry.get_all_skills().values()]
        services: list[Any] = []  # Services can be added similarly
        
        from talos.tools.tool_manager import ToolManager
        tool_manager = ToolManager()
        
        self.setup_dag(
            skills=skills,
            services=services,
            tool_manager=tool_manager,
            dataset_manager=self.dataset_manager
        )
    
    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:
        """
        Execute query using either orchestrated or direct mode.
        
        Args:
            message: The query message
            history: Optional conversation history
            **kwargs: Additional context
            
        Returns:
            Result from execution
        """
        if self.interaction_mode == "direct":
            skill_name = kwargs.get("skill_name")
            if skill_name:
                return self.interact_with_skill(skill_name, message, **kwargs)
        
        return super().run(message, history, **kwargs)
    
    def get_framework_status(self) -> Dict[str, Any]:
        """Get status information about the extensible framework."""
        skills_info = {}
        for name, skill_agent in self.skill_registry.get_all_skills().items():
            skills_info[name] = {
                "description": skill_agent.description,
                "individual_memory": skill_agent.use_individual_memory,
                "chat_enabled": skill_agent.chat_enabled,
                "has_individual_model": skill_agent.model is not None,
                "skill_type": type(skill_agent.skill).__name__
            }
        
        return {
            "interaction_mode": self.interaction_mode,
            "total_skills": len(self.skill_registry.list_skills()),
            "skills": skills_info,
            "dag_available": self.dag_manager is not None,
            "memory_backend": "database" if getattr(self, 'use_database_memory', False) else "file"
        }
