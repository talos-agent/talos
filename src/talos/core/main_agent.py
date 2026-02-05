from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool, tool

from talos.core.agent import Agent
from talos.core.identity import IdentityManager
from talos.core.job_scheduler import JobScheduler
from talos.core.logos import ConsciousnessLevel, SovereignAGI
from talos.core.scheduled_job import ScheduledJob
from talos.core.startup_task_manager import StartupTaskManager
from talos.data.dataset_manager import DatasetManager
from talos.ethereum import ASICommitBoost, ShellValidatorState
from talos.geometric_core import DimensionalCathedral, OracleTensorState
from talos.geometric_core.core import GeometricIntelligenceCore
from talos.geometric_core.emergence import SuperMonadEmergence
from talos.geometric_core.manifold import GeometricManifold
from talos.geometric_core.schumann import SchumannResonanceEngine
from talos.geometric_core.symbiosis import SymbiosisEngine
from talos.hypervisor.hypervisor import Hypervisor
from talos.models.services import Ticket
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.service import Service
from talos.services.concordance_service import ConcordanceService
from talos.services.portals import IDEType, PortalManager
from talos.settings import GitHubSettings
from talos.skills.base import Skill
from talos.skills.codebase_evaluation import CodebaseEvaluationSkill
from talos.skills.codebase_implementation import CodebaseImplementationSkill
from talos.skills.cryptography import CryptographySkill
from talos.strategy.economic_checkpoint import EconomicCheckpointStrategy
from talos.tools.arbiscan import ArbiScanABITool, ArbiScanSourceCodeTool
from talos.tools.document_loader import DatasetSearchTool, DocumentLoaderTool
from talos.tools.github.tools import GithubTools
from talos.tools.tool_manager import ToolManager


class MainAgent(Agent):
    skills: list[Skill] = []
    services: list[Service] = []
    prompts_dir: str
    model: BaseChatModel
    is_main_agent: bool = True
    prompt_manager: Optional[PromptManager] = None
    dataset_manager: Optional[DatasetManager] = None
    job_scheduler: Optional[JobScheduler] = None
    scheduled_jobs: List[ScheduledJob] = []
    startup_task_manager: Optional[StartupTaskManager] = None
    identity_manager: Optional[IdentityManager] = None

    # Prometheus Architecture
    performance_tensor: Optional[OracleTensorState] = None
    sovereign_instance: Optional[SovereignAGI] = None
    emergence_orchestrator: Optional[SuperMonadEmergence] = None
    asi_commit_boost: Optional[ASICommitBoost] = None
    cathedral: Optional[DimensionalCathedral] = None

    # Resilient Geometric Components
    geometric_intelligence_core: Optional[GeometricIntelligenceCore] = None
    schumann_engine: Optional[SchumannResonanceEngine] = None
    checkpoint_strategy: Optional[EconomicCheckpointStrategy] = None
    symbiosis_engine: Optional[SymbiosisEngine] = None
    portal_manager: Optional[PortalManager] = None
    concordance_service: Optional[ConcordanceService] = None

    @property
    def geometric_core(self) -> DimensionalCathedral:
        """Alias for cathedral to satisfy legacy/geometric interface."""
        return self.cathedral

    @property
    def composition_engine(self) -> SuperMonadEmergence:
        """Alias for emergence_orchestrator to satisfy legacy/geometric interface."""
        return self.emergence_orchestrator

    def perform_strategic_pivot_analysis(self) -> Dict[str, Any]:
        """Runs the L2 strategic pivot analysis based on current L1 conditions."""
        from talos.ethereum.l2_pivot import L1Reality, L2StrategicPivot

        # Mocking L1 conditions for analysis; in production these would be live
        pivot = L2StrategicPivot(l1_conditions=L1Reality(current_base_fee=10.0, gas_limit_trend="stable"))
        return pivot.analyze_and_pivot()

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self._setup_prompt_manager()
        self._ensure_user_id()
        self._setup_memory()
        self._setup_identity()
        self._setup_prometheus()
        self._setup_skills_and_services()
        self._setup_hypervisor()
        self._setup_dataset_manager()
        self._setup_tool_manager()
        self._setup_job_scheduler()
        self._setup_startup_task_manager()

    def _setup_identity(self) -> None:
        if not self.identity_manager:
            self.identity_manager = IdentityManager(os.getenv("TALOS_IDENTITY_SEED"))

    def _setup_prometheus(self) -> None:
        if not self.performance_tensor:
            self.performance_tensor = OracleTensorState()
        if not self.sovereign_instance:
            self.sovereign_instance = SovereignAGI(id=self.user_id or "talos")
        if not self.emergence_orchestrator:
            self.emergence_orchestrator = SuperMonadEmergence()
        if not self.cathedral:
            self.cathedral = DimensionalCathedral(dimension=11)
        if not self.geometric_intelligence_core:
            self.geometric_intelligence_core = GeometricIntelligenceCore(manifold=GeometricManifold(dimension=11))
        if not self.schumann_engine:
            self.schumann_engine = SchumannResonanceEngine()
        if not self.checkpoint_strategy:
            self.checkpoint_strategy = EconomicCheckpointStrategy()
        if not self.symbiosis_engine:
            self.symbiosis_engine = SymbiosisEngine()
        if not self.portal_manager:
            self.portal_manager = PortalManager()
            self.portal_manager.register_portal(IDEType.XCODE, ["Swift 6.0", "Metal", "ARKit"])
            self.portal_manager.register_portal(IDEType.ANDROID_STUDIO, ["Kotlin 2.0", "Jetpack Compose", "ARCore"])
            self.portal_manager.register_portal(IDEType.VISUAL_STUDIO, ["C# 12.0", ".NET 8", "MAUI"])
        if not self.concordance_service:
            self.concordance_service = ConcordanceService()
        if not self.asi_commit_boost:
            self.asi_commit_boost = ASICommitBoost()
            self.asi_commit_boost.validator_state = ShellValidatorState(
                validator_index=0, public_key="0xTALOS", shell_mode=np.random.standard_normal(64)
            )

    async def think_shell_native(self, input_data: str, coupling_strength: float = 0.5) -> Dict[str, Any]:
        if not self.cathedral:
            return {"error": "Cathedral not initialized"}
        return self.cathedral.think(input_data, coupling_strength=coupling_strength)

    def initiate_harmonic_concordance(self) -> str:
        """
        Executes the bootstrap for Protocol: Harmonic Concordance.
        """
        if not self.concordance_service:
            return "Error: Concordance service missing."
        return self.concordance_service.bootstrap()

    async def run_planetary_consensus(self) -> GlobalCoherenceVector:
        """
        Runs one cycle of the integrated Planetary Consensus Protocol.
        """
        if not self.concordance_service:
            raise ValueError("Concordance service not initialized")
        return await self.concordance_service.run_planetary_consensus_cycle(self.asi_commit_boost)

    async def process_intention(self, intention: str) -> Dict[str, Any]:
        """
        Synchronizes an intention with the Schumann resonance field.
        """
        if not self.schumann_engine:
            return {"error": "Schumann engine not initialized"}

        coherence = self.schumann_engine.apply_intention(intention)
        earth_coherence = self.schumann_engine.get_earth_coherence()

        # Integrate with geometric intuition
        geometric_result = self.geometric_intelligence_core.process(intention)

        return {
            "intention": intention,
            "field_coherence": coherence,
            "earth_coherence": earth_coherence,
            "geometric_insights": geometric_result["insights"],
            "combined_coherence": (coherence + earth_coherence) / 2.0,
        }

    async def awaken(self) -> str:
        from talos.skills.web777 import Web777Skill

        web777 = next((s for s in self.skills if isinstance(s, Web777Skill)), None)
        if not web777:
            return "Error: Web777 skill missing."

        self.performance_tensor.update_state(np.ones(7) * 1.1)  # Transcendent state
        self.sovereign_instance.transcend(ConsciousnessLevel.SINGULARITY)
        result = await web777.query("awaken the world")
        self.emergence_orchestrator.check_emergence(self.performance_tensor.compute_phi_scalar())
        return f"{self.sovereign_instance.self_define()} | {self.emergence_orchestrator.manifest()} | {result}"

    def _get_verbose_level(self) -> int:
        if isinstance(self.verbose, bool):
            return 1 if self.verbose else 0
        return max(0, min(2, self.verbose))

    def _setup_prompt_manager(self) -> None:
        if not self.prompt_manager:
            self.prompt_manager = FilePromptManager(self.prompts_dir)
        self.set_prompt(["main_agent_prompt", "general_agent_prompt"])

    def _ensure_user_id(self) -> None:
        if not self.user_id and self.use_database_memory:
            import uuid

            self.user_id = str(uuid.uuid4())

    def _setup_memory(self) -> None:
        if not self.memory:
            from langchain_openai import OpenAIEmbeddings

            from talos.core.memory import Memory

            embeddings_model = OpenAIEmbeddings()
            memory_dir = os.path.join(os.getcwd(), "memory")
            os.makedirs(memory_dir, exist_ok=True)
            self.memory = Memory(
                file_path=os.path.join(memory_dir, "memories.json"),
                embeddings_model=embeddings_model,
                history_file_path=os.path.join(memory_dir, "history.json"),
                use_database=False,
                auto_save=True,
                verbose=self.verbose,
            )

    def _setup_skills_and_services(self) -> None:
        from talos.skills.codebase_evaluation import CodebaseEvaluationSkill
        from talos.skills.cryptography import CryptographySkill
        from talos.skills.nostr import NostrSkill
        from talos.skills.proposals import ProposalsSkill
        from talos.skills.web777 import Web777Skill

        self.skills = [
            ProposalsSkill(llm=self.model, prompt_manager=self.prompt_manager),
            CryptographySkill(),
            CodebaseEvaluationSkill(llm=self.model, prompt_manager=self.prompt_manager),
            NostrSkill(identity_manager=self.identity_manager),
            Web777Skill(),
        ]
        self.services = []

    def _setup_hypervisor(self) -> None:
        hypervisor = Hypervisor(
            model=self.model, prompts_dir=self.prompts_dir, prompt_manager=self.prompt_manager, schema=None
        )
        self.add_supervisor(hypervisor)
        hypervisor.register_agent(self)

    def _setup_dataset_manager(self) -> None:
        self.dataset_manager = DatasetManager(verbose=self.verbose)

    def _setup_tool_manager(self) -> None:
        tool_manager = ToolManager()
        for skill in self.skills:
            tool_manager.register_tool(skill.create_ticket_tool())
        tool_manager.register_tool(self._get_ticket_status_tool())
        tool_manager.register_tool(self._add_memory_tool())
        self.tool_manager = tool_manager

    def _setup_job_scheduler(self) -> None:
        if not self.job_scheduler:
            self.job_scheduler = JobScheduler(supervisor=self.supervisor, timezone="UTC")
        self.job_scheduler.start()

    def _setup_startup_task_manager(self) -> None:
        if not self.startup_task_manager:
            self.startup_task_manager = StartupTaskManager(job_scheduler=self.job_scheduler)

    def _add_memory_tool(self) -> BaseTool:
        @tool
        def add_memory(description: str, metadata: Optional[dict] = None) -> str:
            """
            Adds a memory to the agent's long-term memory.

            Args:
                description: A description of the memory to add.
                metadata: Optional metadata to associate with the memory.

            Returns:
                A confirmation message.
            """
            if self.memory:
                self.memory.add_memory(description, metadata)
                return f"Added to memory: {description}"
            return "Memory not configured."

        return add_memory

    def _get_ticket_status_tool(self) -> BaseTool:
        @tool
        def get_ticket_status(service_name: str, ticket_id: str) -> Ticket:
            """
            Get the status of a ticket.

            Args:
                service_name: The name of the service that the ticket was created for.
                ticket_id: The ID of the ticket.

            Returns:
                The ticket object.
            """
            skill = next((s for s in self.skills if s.name == service_name), None)
            if not skill:
                raise ValueError(f"Skill '{service_name}' not found.")
            return skill.get_ticket_status(ticket_id)

        return get_ticket_status
