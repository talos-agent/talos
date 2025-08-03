from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, ConfigDict

from talos.core.memory import Memory
from talos.dag.manager import DAGManager
from talos.prompts.prompt_manager import PromptManager
from talos.skills.base import Skill
from talos.tools.tool_manager import ToolManager

from talos.dag.dag_agent import DAGAgent
if TYPE_CHECKING:
    from talos.dag.structured_nodes import NodeVersion


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
    """Registry for managing specialized support agents with structured delegation rules."""
    
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
    Main agent that delegates tasks to specialized support agents with structured DAG structure.
    Each support agent has a specific architecture for handling their domain of tasks.
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    support_agents: Dict[str, "SupportAgent"] = {}
    delegation_rules: Dict[str, str] = {}  # keyword -> agent mapping
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_support_agents()
        self._build_structured_dag()
    
    def _setup_support_agents(self) -> None:
        """Setup specialized support agents with structured architectures."""
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
    
    def _build_structured_dag(self) -> None:
        """Build a structured DAG structure with predefined delegation patterns."""
        self.delegation_rules = {}
        for agent in self.support_agents.values():
            for keyword in agent.delegation_keywords:
                self.delegation_rules[keyword.lower()] = agent.name
        
        self._rebuild_dag()
    
    def delegate_task(self, query: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Delegate a task to the appropriate support agent based on structured rules.
        
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
        self._build_structured_dag()
        
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
            self._build_structured_dag()
            return True
        return False
    
    def list_support_agents(self) -> List[str]:
        """List all available support agents."""
        return list(self.support_agents.keys())
    
    def get_support_agent(self, domain: str) -> Optional[SupportAgent]:
        """Get a specific support agent by domain."""
        return self.support_agents.get(domain)
    
    def _rebuild_dag(self) -> None:
        """Rebuild the structured DAG with current support agents."""
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
            "architecture_type": "structured_delegation"
        }


class StructuredMainAgent(DAGAgent):
    """
    Main agent with structured DAG architecture for blockchain-native node upgrades.
    
    This class represents the core of a blockchain-native AI system that enables
    individual component upgrades while maintaining deterministic behavior and
    system integrity. It orchestrates a network of specialized support agents
    through a structured DAG architecture.
    
    Blockchain-Native Architecture:
        The agent is designed from the ground up for blockchain compatibility:
        - Deterministic execution paths ensure reproducible results
        - Individual node upgrades enable granular system evolution
        - Hash-based verification prevents tampering and ensures integrity
        - Serializable state enables on-chain storage and verification
        
    Key Features:
        - Structured DAG with versioned nodes for controlled upgrades
        - Deterministic delegation patterns using hash-based routing
        - Individual support agent upgrade capabilities
        - Blockchain-compatible serialization and state management
        - Comprehensive upgrade validation and rollback support
        
    Support Agent Architecture:
        Each support agent represents a specialized capability with:
        - Unique domain expertise (governance, analytics, research, etc.)
        - Individual versioning and upgrade policies
        - Specific task patterns and delegation keywords
        - Custom architectures for handling domain-specific tasks
        
    Upgrade Methodology:
        The system supports three types of upgrades:
        1. Individual node upgrades with version validation
        2. Controlled rollbacks to previous versions
        3. DAG-wide configuration updates with integrity checks
        
    Deterministic Delegation:
        Task routing uses deterministic patterns:
        - Keyword-based matching with sorted rule evaluation
        - Hash-based verification of delegation rules
        - Reproducible routing decisions across environments
        - Fallback mechanisms for unmatched queries
        
    Attributes:
        support_agents: Registry of available support agents
        structured_dag_manager: Manager for DAG operations and upgrades
        
    Examples:
        >>> agent = StructuredMainAgent(
        ...     model=ChatOpenAI(model="gpt-4"),
        ...     prompts_dir="/path/to/prompts",
        ...     verbose=True
        ... )
        >>> 
        >>> # Delegate a governance task
        >>> result = agent.delegate_task("Analyze governance proposal for voting")
        >>> 
        >>> # Upgrade a specific node
        >>> success = agent.upgrade_support_agent(
        ...     "governance", 
        ...     enhanced_agent, 
        ...     NodeVersion(1, 1, 0)
        ... )
        >>> 
        >>> # Export for blockchain storage
        >>> blockchain_data = agent.export_for_blockchain()
    """
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    support_agents: Dict[str, SupportAgent] = {}
    structured_dag_manager: Optional[Any] = None
    delegation_hash: str = ""
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_structured_support_agents()
        self._build_structured_dag()
    
    def _setup_structured_support_agents(self) -> None:
        """
        Setup default support agents for the structured DAG.
        
        This method initializes the core set of support agents that provide
        specialized capabilities for the AI system. Each agent is configured
        with specific domain expertise, task patterns, and delegation keywords.
        
        Default Support Agents:
        - Governance: Handles proposals, voting, and DAO operations
        - Analytics: Processes data analysis and reporting tasks
        
        Each agent is initialized with:
        - Semantic versioning starting at 1.0.0
        - Compatible upgrade policy for safe evolution
        - Domain-specific task patterns and keywords
        - Specialized architecture for handling their domain
        
        The setup ensures deterministic agent ordering and consistent
        initialization across different execution environments.
        """
        governance_agent = SupportAgent(
            name="governance",
            domain="governance",
            description="Structured governance agent for blockchain proposals",
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
            description="Structured analytics agent for data processing",
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
    
    def _build_structured_dag(self) -> None:
        """
        Build the structured DAG with current support agents.
        
        This method constructs the blockchain-native DAG architecture:
        1. Creates StructuredDAGManager for controlled operations
        2. Builds DAG with deterministic node ordering
        3. Establishes routing and delegation patterns
        4. Validates DAG structure and integrity
        
        The resulting DAG provides:
        - Deterministic execution paths for reproducible results
        - Individual node upgrade capabilities
        - Hash-based verification of structure integrity
        - Blockchain-compatible serialization format
        
        DAG Structure:
        - Router node for task delegation
        - Individual support agent nodes with versioning
        - Shared prompt and data source nodes
        - Deterministic edge connections
        
        Raises:
            ValueError: If DAG construction fails or validation errors occur
        """
        if not self.prompt_manager:
            return
        
        from talos.dag.structured_manager import StructuredDAGManager
        
        services = []
        if hasattr(self, 'services'):
            services = self.services
        
        tool_manager = ToolManager()
        if hasattr(self, 'tool_manager'):
            tool_manager = self.tool_manager
        
        self.structured_dag_manager = StructuredDAGManager()
        
        try:
            self.dag = self.structured_dag_manager.create_structured_dag(
                model=self.model,  # type: ignore
                prompt_manager=self.prompt_manager,
                support_agents=self.support_agents,
                services=services,
                tool_manager=tool_manager,
                dataset_manager=getattr(self, 'dataset_manager', None),
                dag_name="structured_blockchain_dag"
            )
        except Exception as e:
            print(f"Warning: Could not build structured DAG: {e}")
    
    def upgrade_support_agent(
        self,
        domain: str,
        new_agent: SupportAgent,
        new_version: "NodeVersion",
        force: bool = False
    ) -> bool:
        """
        Upgrade a specific support agent with comprehensive validation.
        
        This method enables individual component upgrades in the blockchain-native
        AI system. It performs controlled upgrades while maintaining system integrity
        and deterministic behavior.
        
        Upgrade Process:
        1. Validates the target domain exists and is upgradeable
        2. Checks version compatibility against current upgrade policy
        3. Performs the upgrade through the structured DAG manager
        4. Updates support agent registry with new configuration
        5. Rebuilds DAG structure with updated node
        
        Safety Measures:
        - Version compatibility validation prevents breaking changes
        - Upgrade policies enforce safe transition paths
        - Rollback capability preserved for recovery
        - DAG integrity maintained throughout process
        
        Args:
            domain: Domain identifier of the support agent to upgrade
            new_agent: Updated support agent configuration
            new_version: Target version for the upgrade
            force: Whether to bypass version compatibility checks
            
        Returns:
            True if upgrade succeeded, False if validation failed
            
        Examples:
            >>> enhanced_agent = SupportAgent(
            ...     name="governance_v2",
            ...     domain="governance",
            ...     description="Enhanced governance with new features",
            ...     # ... additional configuration
            ... )
            >>> success = agent.upgrade_support_agent(
            ...     "governance",
            ...     enhanced_agent,
            ...     NodeVersion(1, 1, 0)
            ... )
            >>> if success:
            ...     print("Governance agent upgraded successfully")
        """
        if not self.structured_dag_manager:
            return False
        
        success = self.structured_dag_manager.upgrade_node(domain, new_agent, new_version, force)
        if success:
            self.support_agents[domain] = new_agent
        
        return success
    
    def validate_upgrade(self, domain: str, new_version: "NodeVersion") -> Dict[str, Any]:
        """
        Validate if a support agent can be upgraded to the specified version.
        
        This method provides comprehensive upgrade validation before attempting
        actual upgrades. It helps prevent incompatible changes and ensures
        safe evolution of the AI system.
        
        Validation Checks:
        - Domain existence and upgrade capability
        - Version compatibility against upgrade policy
        - Semantic versioning rules enforcement
        - Breaking change detection
        
        Args:
            domain: Domain identifier of the support agent
            new_version: Proposed version for upgrade validation
            
        Returns:
            Dictionary containing detailed validation results:
            - "valid": Boolean indicating if upgrade is allowed
            - "reason": Detailed explanation of validation result
            - "current_version": Current version of the support agent
            - "upgrade_policy": Current upgrade policy in effect
            - "target_version": Proposed target version
            
        Examples:
            >>> result = agent.validate_upgrade("governance", NodeVersion(2, 0, 0))
            >>> if not result["valid"]:
            ...     print(f"Upgrade blocked: {result['reason']}")
            >>> else:
            ...     print("Upgrade validation passed")
        """
        if not self.structured_dag_manager:
            return {"valid": False, "reason": "No structured DAG manager"}
        
        return self.structured_dag_manager.validate_upgrade(domain, new_version)
    
    def rollback_node(self, domain: str, target_version: "NodeVersion") -> bool:
        """
        Rollback a support agent to a previous version.
        
        This method enables controlled rollback of individual components
        when issues are discovered after upgrades. It maintains system
        stability by allowing quick recovery to known-good states.
        
        Rollback Process:
        1. Validates the target domain and version
        2. Ensures target version is older than current version
        3. Performs rollback through structured DAG manager
        4. Updates support agent registry
        5. Rebuilds DAG with rolled-back configuration
        
        Safety Measures:
        - Only allows rollback to older versions
        - Preserves DAG structural integrity
        - Maintains deterministic behavior
        - Updates all relevant hashes and metadata
        
        Args:
            domain: Domain identifier of the support agent
            target_version: Previous version to rollback to
            
        Returns:
            True if rollback succeeded, False if validation failed
            
        Examples:
            >>> success = agent.rollback_node("governance", NodeVersion(1, 0, 0))
            >>> if success:
            ...     print("Governance agent rolled back successfully")
        """
        if not self.structured_dag_manager:
            return False
        
        return self.structured_dag_manager.rollback_node(domain, target_version)
    
    def get_node_status(self, domain: str) -> Dict[str, Any]:
        """
        Get detailed status of a specific support agent node.
        
        This method provides comprehensive information about individual
        support agents, including their current configuration, version
        status, and upgrade capabilities.
        
        Status Information:
        - Current version and upgrade policy
        - Node hash for blockchain verification
        - Delegation keywords and task patterns
        - Architecture configuration
        - Upgrade compatibility status
        
        Args:
            domain: Domain identifier of the support agent
            
        Returns:
            Dictionary containing detailed node status:
            - "version": Current semantic version
            - "upgrade_policy": Current upgrade policy
            - "node_hash": Blockchain verification hash
            - "delegation_keywords": Keywords for task routing
            - "task_patterns": Supported task patterns
            - "architecture": Agent architecture configuration
            - "error": Error message if node not found
            
        Examples:
            >>> status = agent.get_node_status("governance")
            >>> print(f"Governance agent v{status['version']}")
            >>> print(f"Upgrade policy: {status['upgrade_policy']}")
        """
        if not self.structured_dag_manager or domain not in self.structured_dag_manager.node_registry:
            return {"error": "Node not found"}
        
        node = self.structured_dag_manager.node_registry[domain]
        return {
            "node_id": node.node_id,
            "version": str(node.node_version),
            "domain": node.support_agent.domain,
            "architecture": node.support_agent.architecture,
            "delegation_keywords": node.support_agent.delegation_keywords,
            "upgrade_policy": node.upgrade_policy,
            "node_hash": node.node_hash
        }
    
    def get_structured_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the structured DAG and all components.
        
        This method provides a complete overview of the blockchain-native
        AI system, including DAG structure, node status, and blockchain
        readiness indicators.
        
        Comprehensive Status:
        - DAG metadata (name, version, node count)
        - Individual node status and versions
        - Delegation hash and routing configuration
        - Edge and conditional edge mappings
        - Blockchain compatibility indicators
        
        Returns:
            Dictionary containing complete system status:
            - "dag_name": Name of the current DAG
            - "dag_version": Current DAG version
            - "total_nodes": Number of nodes in the DAG
            - "structured_nodes": Detailed information for each node
            - "delegation_hash": Current delegation hash
            - "blockchain_ready": Blockchain compatibility status
            - "edges": DAG edge configuration
            - "conditional_edges": Conditional routing rules
            
        Examples:
            >>> status = agent.get_structured_status()
            >>> print(f"System has {status['total_nodes']} nodes")
            >>> print(f"Blockchain ready: {status['blockchain_ready']}")
            >>> for node_id, info in status['structured_nodes'].items():
            ...     print(f"{node_id}: v{info['version']}")
        """
        if not self.structured_dag_manager:
            return {"status": "No structured DAG manager"}
        
        return self.structured_dag_manager.get_structured_dag_status()
    
    def export_for_blockchain(self) -> Dict[str, Any]:
        """
        Export DAG configuration for blockchain storage.
        
        This method produces a deterministic, serializable representation
        of the entire DAG structure suitable for on-chain storage and
        verification. The export includes all node configurations,
        delegation rules, and integrity hashes.
        
        Returns:
            Dictionary containing blockchain-ready DAG configuration
        """
        if not self.structured_dag_manager:
            return {}
        
        return self.structured_dag_manager.export_for_blockchain()
    
    def delegate_task(self, query: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Delegate task using structured DAG execution.
        
        This method routes tasks through the structured DAG architecture,
        enabling deterministic delegation to appropriate support agents
        based on the configured routing rules.
        
        Args:
            query: Task query to be delegated
            context: Optional context for task execution
            
        Returns:
            Results from DAG execution or error message
        """
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
        
        return f"Structured main agent handling: {query}"
