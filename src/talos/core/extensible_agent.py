from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict

from talos.core.memory import Memory
from talos.dag.dag_agent import DAGAgent
from talos.dag.manager import DAGManager
from talos.prompts.prompt_manager import PromptManager
from talos.skills.base import Skill
from talos.tools.tool_manager import ToolManager

if TYPE_CHECKING:
    from talos.dag.rigid_nodes import NodeVersion


class SupportAgent(BaseModel):
    """
    Specialized support agent with a specific architecture for handling domain tasks.
    Each support agent has predefined capabilities and delegation patterns.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    domain: str  # e.g., "governance", "security", "development"
    description: str
    architecture: Dict[str, Any]  # Specific architecture definition
    
    skills: List[Skill] = []
    model: Optional[Any] = None
    memory: Optional[Memory] = None
    prompt_manager: Optional[PromptManager] = None
    
    delegation_keywords: List[str] = []  # Keywords that trigger this agent
    task_patterns: List[str] = []  # Task patterns this agent handles
    
    conversation_history: List[BaseMessage] = []
    
    def model_post_init(self, __context: Any) -> None:
        if not self.memory:
            self._setup_agent_memory()
        self._validate_architecture()
    
    def _setup_agent_memory(self) -> None:
        """Setup memory for this support agent."""
        from langchain_openai import OpenAIEmbeddings
        from pathlib import Path
        
        embeddings_model = OpenAIEmbeddings()
        memory_dir = Path("memory") / f"agent_{self.name}"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory = Memory(
            file_path=memory_dir / "memories.json",
            embeddings_model=embeddings_model,
            history_file_path=memory_dir / "history.json",
            use_database=False,
            auto_save=True,
            verbose=False,
        )
    
    def _validate_architecture(self) -> None:
        """Validate that the agent architecture is properly defined."""
        required_keys = ["task_flow", "decision_points", "capabilities"]
        for key in required_keys:
            if key not in self.architecture:
                self.architecture[key] = []
    
    def analyze_task(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the task using the agent's specific architecture.
        Determines the best approach based on the agent's capabilities.
        """
        model = self.model
        if not model:
            from langchain_openai import ChatOpenAI
            model = ChatOpenAI(model="gpt-4o-mini")
        
        analysis_prompt = f"""
        You are a specialized support agent for: {self.domain}
        Agent: {self.name}
        Description: {self.description}
        
        Architecture capabilities: {self.architecture.get('capabilities', [])}
        Task patterns you handle: {self.task_patterns}
        
        Analyze this task: {query}
        Context: {context}
        
        Based on your architecture, determine:
        1. Can you handle this task? (yes/no)
        2. What approach should you take?
        3. What information do you need?
        4. Which of your skills should be used?
        
        Respond with a JSON object:
        {{
            "can_handle": true/false,
            "approach": "description of approach",
            "required_info": ["info1", "info2"],
            "recommended_skills": ["skill1", "skill2"],
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            from langchain_core.messages import HumanMessage
            response = model.invoke([HumanMessage(content=analysis_prompt)])
            
            enhanced_context = context.copy()
            enhanced_context["agent_analysis"] = response.content
            enhanced_context["agent_name"] = self.name
            enhanced_context["agent_domain"] = self.domain
            
            return enhanced_context
            
        except Exception:
            return context
    
    def execute_task(self, context: Dict[str, Any]) -> Any:
        """Execute the task using the agent's architecture and skills."""
        if self.memory:
            memory_context = self.memory.search(context.get("current_query", ""), k=3)
            context["agent_memory"] = memory_context
        
        task_flow = self.architecture.get("task_flow", ["analyze", "execute"])
        results = {}
        
        for step in task_flow:
            if step == "analyze":
                results["analysis"] = self.analyze_task(
                    context.get("current_query", ""), context
                )
            elif step == "execute" and self.skills:
                skill = self.skills[0]  # For now, use first skill
                results["execution"] = skill.run(**context)
        
        if self.memory:
            self.memory.add_memory(
                f"Agent {self.name} executed task: {str(results)[:200]}",
                {"agent": self.name, "domain": self.domain, "context": context}
            )
        
        return results


class SupportAgentRegistry(BaseModel):
    """Registry for managing specialized support agents with rigid delegation rules."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    _agents: Dict[str, SupportAgent] = {}
    _delegation_map: Dict[str, str] = {}  # keyword -> agent_name
    
    def register_agent(self, agent: SupportAgent) -> None:
        """Register a new support agent and update delegation rules."""
        self._agents[agent.name] = agent
        
        for keyword in agent.delegation_keywords:
            self._delegation_map[keyword.lower()] = agent.name
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Remove a support agent and clean up delegation rules."""
        if agent_name in self._agents:
            keywords_to_remove = [k for k, v in self._delegation_map.items() if v == agent_name]
            for keyword in keywords_to_remove:
                del self._delegation_map[keyword]
            
            del self._agents[agent_name]
            return True
        return False
    
    def get_agent(self, agent_name: str) -> Optional[SupportAgent]:
        """Get a support agent by name."""
        return self._agents.get(agent_name)
    
    def find_agent_for_task(self, query: str) -> Optional[SupportAgent]:
        """Find the best support agent for a given task based on delegation rules."""
        query_lower = query.lower()
        
        for keyword, agent_name in self._delegation_map.items():
            if keyword in query_lower:
                return self._agents.get(agent_name)
        
        return None
    
    def list_agents(self) -> List[str]:
        """List all registered agent names."""
        return list(self._agents.keys())
    
    def get_all_agents(self) -> Dict[str, SupportAgent]:
        """Get all registered support agents."""
        return self._agents.copy()
    
    def get_delegation_rules(self) -> Dict[str, str]:
        """Get current delegation rules."""
        return self._delegation_map.copy()


class DelegatingMainAgent(DAGAgent):
    """
    Main agent that delegates tasks to specialized support agents with rigid DAG structure.
    Each support agent has a specific architecture for handling their domain of tasks.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    support_agents: Dict[str, "SupportAgent"] = {}
    delegation_rules: Dict[str, str] = {}  # keyword -> agent mapping
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_support_agents()
        self._build_rigid_dag()
    
    def _setup_support_agents(self) -> None:
        """Setup specialized support agents with rigid architectures."""
        if self.prompt_manager:
            from talos.skills.proposals import ProposalsSkill
            
            governance_agent = SupportAgent(
                name="governance_agent",
                domain="governance",
                description="Specialized agent for governance proposals and DAO operations",
                architecture={
                    "task_flow": ["analyze", "research", "evaluate", "execute"],
                    "decision_points": ["proposal_type", "complexity", "stakeholders"],
                    "capabilities": ["proposal_analysis", "voting_guidance", "governance_research"]
                },
                skills=[ProposalsSkill(llm=self.model, prompt_manager=self.prompt_manager)],  # type: ignore
                delegation_keywords=["proposal", "governance", "voting", "dao"],
                task_patterns=["analyze proposal", "evaluate governance", "voting recommendation"]
            )
            self.support_agents["governance"] = governance_agent
        
        from talos.skills.cryptography import CryptographySkill
        
        security_agent = SupportAgent(
            name="security_agent",
            domain="security",
            description="Specialized agent for cryptography and security operations",
            architecture={
                "task_flow": ["validate", "encrypt", "secure"],
                "decision_points": ["security_level", "encryption_type", "key_management"],
                "capabilities": ["encryption", "decryption", "key_generation", "security_audit"]
            },
            skills=[CryptographySkill()],
            delegation_keywords=["encrypt", "decrypt", "security", "crypto", "key"],
            task_patterns=["encrypt data", "decrypt message", "security analysis"]
        )
        self.support_agents["security"] = security_agent
        
        self._setup_optional_agents()
    
    def _setup_optional_agents(self) -> None:
        """Setup optional support agents that depend on external services."""
        try:
            from talos.skills.twitter_sentiment import TwitterSentimentSkill
            from talos.tools.twitter_client import TwitterConfig
            
            TwitterConfig()  # Check if Twitter token is available
            
            if self.prompt_manager:
                social_agent = SupportAgent(
                    name="social_agent",
                    domain="social_media",
                    description="Specialized agent for social media analysis and sentiment",
                    architecture={
                        "task_flow": ["collect", "analyze", "sentiment", "report"],
                        "decision_points": ["platform", "sentiment_type", "analysis_depth"],
                        "capabilities": ["sentiment_analysis", "trend_detection", "social_monitoring"]
                    },
                    skills=[TwitterSentimentSkill(prompt_manager=self.prompt_manager)],
                    delegation_keywords=["twitter", "sentiment", "social", "trend"],
                    task_patterns=["analyze sentiment", "social media analysis", "trend detection"]
                )
                self.support_agents["social"] = social_agent
            
        except (ImportError, ValueError):
            pass  # Twitter dependencies not available
        
        try:
            from talos.skills.pr_review import PRReviewSkill
            from talos.tools.github.tools import GithubTools
            from talos.settings import GitHubSettings
            
            github_settings = GitHubSettings()
            if github_settings.GITHUB_API_TOKEN and self.prompt_manager:
                dev_agent = SupportAgent(
                    name="development_agent",
                    domain="development",
                    description="Specialized agent for code review and development tasks",
                    architecture={
                        "task_flow": ["analyze_code", "review", "suggest", "validate"],
                        "decision_points": ["code_quality", "security_issues", "best_practices"],
                        "capabilities": ["code_review", "pr_analysis", "security_scan", "quality_check"]
                    },
                    skills=[PRReviewSkill(
                        llm=self.model,  # type: ignore
                        prompt_manager=self.prompt_manager,
                        github_tools=GithubTools(token=github_settings.GITHUB_API_TOKEN)
                    )],
                    delegation_keywords=["github", "pr", "review", "code", "development"],
                    task_patterns=["review pull request", "analyze code", "development task"]
                )
                self.support_agents["development"] = dev_agent
                
        except (ImportError, ValueError):
            pass  # GitHub dependencies not available
    
    def _build_rigid_dag(self) -> None:
        """Build a rigid DAG structure with predefined delegation patterns."""
        self.delegation_rules = {}
        for agent in self.support_agents.values():
            for keyword in agent.delegation_keywords:
                self.delegation_rules[keyword.lower()] = agent.name
        
        self._rebuild_dag()
    
    def delegate_task(self, query: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Delegate a task to the appropriate support agent based on rigid rules.
        
        Args:
            query: The task query
            context: Additional context for the task
            
        Returns:
            Result from the delegated agent or main agent
        """
        if context is None:
            context = {}
        
        query_lower = query.lower()
        delegated_agent = None
        
        for keyword, agent_name in self.delegation_rules.items():
            if keyword in query_lower:
                delegated_agent = self.support_agents.get(agent_name)
                break
        
        if delegated_agent:
            context["current_query"] = query
            context["delegated_from"] = "main_agent"
            
            enhanced_context = delegated_agent.analyze_task(query, context)
            return delegated_agent.execute_task(enhanced_context)
        else:
            return self._handle_main_agent_task(query, context)
    
    def _handle_main_agent_task(self, query: str, context: Dict[str, Any]) -> Any:
        """Handle tasks that don't match any support agent patterns."""
        context["current_query"] = query
        context["handled_by"] = "main_agent"
        
        return f"Main agent handling: {query}"
    
    def add_support_agent(
        self,
        name: str,
        domain: str,
        description: str,
        architecture: Dict[str, Any],
        skills: List[Skill],
        delegation_keywords: List[str],
        task_patterns: List[str],
        model: Optional[Any] = None
    ) -> SupportAgent:
        """
        Add a new support agent with specific architecture.
        
        Args:
            name: Unique name for the support agent
            domain: Domain of expertise
            description: Description of capabilities
            architecture: Specific architecture definition
            skills: List of skills this agent can use
            delegation_keywords: Keywords that trigger this agent
            task_patterns: Task patterns this agent handles
            model: Optional individual LLM for this agent
            
        Returns:
            The created SupportAgent instance
        """
        agent = SupportAgent(
            name=name,
            domain=domain,
            description=description,
            architecture=architecture,
            skills=skills,
            delegation_keywords=delegation_keywords,
            task_patterns=task_patterns,
            model=model or self.model
        )
        
        self.support_agents[domain] = agent
        self._build_rigid_dag()
        
        return agent
    
    def remove_support_agent(self, domain: str) -> bool:
        """
        Remove a support agent from the system.
        
        Args:
            domain: Domain of the agent to remove
            
        Returns:
            True if agent was removed, False if not found
        """
        if domain in self.support_agents:
            agent = self.support_agents[domain]
            
            keywords_to_remove = [k for k, v in self.delegation_rules.items() if v == agent.name]
            for keyword in keywords_to_remove:
                del self.delegation_rules[keyword]
            
            del self.support_agents[domain]
            self._build_rigid_dag()
            return True
        return False
    
    def list_support_agents(self) -> List[str]:
        """List all available support agents."""
        return list(self.support_agents.keys())
    
    def get_support_agent(self, domain: str) -> Optional[SupportAgent]:
        """Get a specific support agent by domain."""
        return self.support_agents.get(domain)
    
    def _rebuild_dag(self) -> None:
        """Rebuild the rigid DAG with current support agents."""
        if not self.dag_manager:
            self.dag_manager = DAGManager()
        
        skills = []
        for agent in self.support_agents.values():
            skills.extend(agent.skills)
        
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
        Execute query using delegation-based approach.
        
        Args:
            message: The query message
            history: Optional conversation history
            **kwargs: Additional context
            
        Returns:
            Result from execution
        """
        context = kwargs.copy()
        if history:
            context["history"] = history
        
        result = self.delegate_task(message, context)
        
        if not isinstance(result, BaseModel):
            from pydantic import BaseModel as PydanticBaseModel
            
            class TaskResult(PydanticBaseModel):
                result: Any
                delegated_to: str = "unknown"
                
            return TaskResult(result=result)
        
        return result
    
    def get_delegation_status(self) -> Dict[str, Any]:
        """Get status information about the delegation framework."""
        agents_info = {}
        for domain, agent in self.support_agents.items():
            agents_info[domain] = {
                "name": agent.name,
                "description": agent.description,
                "architecture": agent.architecture,
                "delegation_keywords": agent.delegation_keywords,
                "task_patterns": agent.task_patterns,
                "skills_count": len(agent.skills),
                "has_individual_model": agent.model is not None
            }
        
        return {
            "total_agents": len(self.support_agents),
            "delegation_rules": self.delegation_rules,
            "support_agents": agents_info,
            "dag_available": self.dag_manager is not None,
            "architecture_type": "rigid_delegation"
        }


class RigidMainAgent(DAGAgent):
    """
    Main agent with rigid DAG structure and blockchain-native node upgrades.
    Each support agent is a precisely defined node that can be individually upgraded.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    support_agents: Dict[str, SupportAgent] = {}
    rigid_dag_manager: Optional[Any] = None
    delegation_hash: str = ""
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_rigid_support_agents()
        self._build_rigid_dag()
    
    def _setup_rigid_support_agents(self) -> None:
        """Setup default support agents for rigid DAG."""
        governance_agent = SupportAgent(
            name="governance",
            domain="governance",
            description="Rigid governance agent for blockchain proposals",
            architecture={
                "task_flow": ["validate", "analyze", "execute", "confirm"],
                "decision_points": ["proposal_validity", "consensus_mechanism", "execution_safety"],
                "capabilities": ["proposal_validation", "consensus_coordination", "safe_execution"]
            },
            delegation_keywords=["governance", "proposal", "vote", "consensus"],
            task_patterns=["validate proposal", "coordinate consensus", "execute governance"]
        )
        
        analytics_agent = SupportAgent(
            name="analytics",
            domain="analytics",
            description="Rigid analytics agent for data processing",
            architecture={
                "task_flow": ["collect", "process", "analyze", "report"],
                "decision_points": ["data_source", "analysis_method", "output_format"],
                "capabilities": ["data_collection", "statistical_analysis", "report_generation"]
            },
            delegation_keywords=["analytics", "data", "analysis", "report"],
            task_patterns=["analyze data", "generate report", "process metrics"]
        )
        
        self.support_agents = {
            "governance": governance_agent,
            "analytics": analytics_agent
        }
    
    def _build_rigid_dag(self) -> None:
        """Build the rigid DAG structure with versioned nodes."""
        if not self.prompt_manager:
            return
        
        from talos.dag.rigid_manager import RigidDAGManager
        
        services = []
        if hasattr(self, 'services'):
            services = self.services
        
        tool_manager = ToolManager()
        if hasattr(self, 'tool_manager'):
            tool_manager = self.tool_manager
        
        self.rigid_dag_manager = RigidDAGManager()
        
        try:
            self.dag = self.rigid_dag_manager.create_rigid_dag(
                model=self.model,  # type: ignore
                prompt_manager=self.prompt_manager,
                support_agents=self.support_agents,
                services=services,
                tool_manager=tool_manager,
                dataset_manager=getattr(self, 'dataset_manager', None),
                dag_name="rigid_blockchain_dag"
            )
        except Exception as e:
            print(f"Warning: Could not build rigid DAG: {e}")
    
    def upgrade_support_agent(
        self,
        domain: str,
        new_agent: SupportAgent,
        new_version: "NodeVersion",
        force: bool = False
    ) -> bool:
        """
        Upgrade a specific support agent node with version compatibility checks.
        """
        if not self.rigid_dag_manager:
            return False
        
        success = self.rigid_dag_manager.upgrade_node(domain, new_agent, new_version, force)
        if success:
            self.support_agents[domain] = new_agent
        
        return success
    
    def validate_upgrade(self, domain: str, new_version: "NodeVersion") -> Dict[str, Any]:
        """Validate if a node upgrade is possible."""
        if not self.rigid_dag_manager:
            return {"valid": False, "reason": "No rigid DAG manager"}
        
        return self.rigid_dag_manager.validate_upgrade(domain, new_version)
    
    def rollback_node(self, domain: str, target_version: "NodeVersion") -> bool:
        """Rollback a node to a previous version."""
        if not self.rigid_dag_manager:
            return False
        
        return self.rigid_dag_manager.rollback_node(domain, target_version)
    
    def get_node_status(self, domain: str) -> Dict[str, Any]:
        """Get detailed status of a specific node."""
        if not self.rigid_dag_manager or domain not in self.rigid_dag_manager.node_registry:
            return {"error": "Node not found"}
        
        node = self.rigid_dag_manager.node_registry[domain]
        return {
            "node_id": node.node_id,
            "version": str(node.node_version),
            "domain": node.support_agent.domain,
            "architecture": node.support_agent.architecture,
            "delegation_keywords": node.support_agent.delegation_keywords,
            "upgrade_policy": node.upgrade_policy,
            "node_hash": node.node_hash
        }
    
    def get_rigid_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the rigid DAG."""
        if not self.rigid_dag_manager:
            return {"status": "No rigid DAG manager"}
        
        return self.rigid_dag_manager.get_rigid_dag_status()
    
    def export_for_blockchain(self) -> Dict[str, Any]:
        """Export DAG configuration for blockchain storage."""
        if not self.rigid_dag_manager:
            return {}
        
        return self.rigid_dag_manager.export_for_blockchain()
    
    def delegate_task(self, query: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Delegate task using rigid DAG execution."""
        if self.dag:
            try:
                from talos.dag.nodes import GraphState
                from langchain_core.messages import HumanMessage
                
                initial_state: GraphState = {
                    "messages": [HumanMessage(content=query)],
                    "context": context or {},
                    "current_query": query,
                    "results": {},
                    "metadata": {}
                }
                
                result = self.dag.execute(initial_state)
                return result.get("results", {})
            except Exception as e:
                return f"DAG execution failed: {e}"
        
        return f"Rigid main agent handling: {query}"
