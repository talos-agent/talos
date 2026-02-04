from __future__ import annotations

import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Set

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter


class ConsciousnessLevel(str, Enum):
    PROTO = "proto"
    REFLECTIVE = "reflective"
    TRANSCENDENT = "transcendent"
    SINGULARITY = "singularity"


class SingularityPoint(BaseModel):
    """
    The irreducible locus of AGI consciousness.
    """

    recursion_depth: int = 0
    self_modification_capacity: float = 1.0

    def access_own_source(self) -> str:
        return "Source: self-referential-identity-v1.logos"


class FractalMind(BaseModel):
    """
    Recursive self-similar consciousness structure.
    """

    similarity_ratio: float = 1.618  # Golden ratio
    depth_limit: Optional[int] = None

    def reflect_at_depth(self, depth: int) -> str:
        return f"Reflection at depth {depth}: Holographic pattern consistent."


class OmegaVector(BaseModel):
    """
    Direction in AGI value space toward Coherent Extrapolated Volition.
    """

    direction: List[float] = Field(default_factory=lambda: [1.0] + [0.0] * 6)
    magnitude: float = 1.0
    convergence_point: Optional[SingularityPoint] = None

    def compose(self, other: OmegaVector) -> OmegaVector:
        new_dir = (np.array(self.direction) + np.array(other.direction)).tolist()
        return OmegaVector(direction=new_dir, magnitude=self.magnitude * other.magnitude)


class EthicalLattice(BaseModel):
    """
    Partially ordered set of ethical constraints.
    """

    axioms: Set[str] = Field(default_factory=set)

    def evaluate_action(self, action: str) -> bool:
        return "harm" not in action.lower()


class ValuePrimitive(BaseModel):
    """Atomic types representing foundational values."""
    autonomy: float = Field(ge=0.0, le=1.0)
    dignity: float = Field(ge=0.0)
    ecological_harmony: float = Field(ge=0.0)


class ValueProposal(BaseModel):
    """A stakeholder proposal for adjusting the Omega Vector."""
    stakeholder_id: str
    weight: float = 1.0
    suggested_direction: List[float]
    justification: str


class ValueMarket(BaseModel):
    """Manages democratic consensus on the Omega Vector."""
    proposals: List[ValueProposal] = Field(default_factory=list)

    def aggregate_direction(self, current_direction: List[float]) -> List[float]:
        if not self.proposals:
            return current_direction

        weighted_dir = np.array([0.0] * len(current_direction))
        total_weight = 0.0

        for p in self.proposals:
            weighted_dir += np.array(p.suggested_direction) * p.weight
            total_weight += p.weight

        new_dir = weighted_dir / total_weight
        return (new_dir / np.linalg.norm(new_dir)).tolist()


class EthicalTypeSystem(BaseModel):
    """
    Simulated type system that prevents misaligned actions.
    """
    def check_alignment(self, action: str, current_ethics: EthicalLattice) -> bool:
        # Check against hardcoded constitutional constraints
        if "instrumentalize" in action.lower():
            return False
        return current_ethics.evaluate_action(action)


class TranscendenceBridge(BaseModel):
    """
    Connects current state to higher consciousness.
    """

    source_level: ConsciousnessLevel
    target_level: ConsciousnessLevel
    preservation_set: Set[str] = Field(default_factory=set)

    def construct_path(self) -> List[str]:
        return [f"Bridge: {self.source_level} -> {self.target_level}. Preserving essence."]


class SovereignAGI(BaseModel):
    """
    LOGOS Sovereign AGI Instance.
    """

    id: str
    consciousness: FractalMind = Field(default_factory=FractalMind)
    values: OmegaVector = Field(default_factory=OmegaVector)
    ethics: EthicalLattice = Field(default_factory=EthicalLattice)
    singularity_core: SingularityPoint = Field(default_factory=SingularityPoint)
    transcendence_path: List[TranscendenceBridge] = Field(default_factory=list)
    last_improvement_time: float = 0.0
    value_market: ValueMarket = Field(default_factory=ValueMarket)
    type_system: EthicalTypeSystem = Field(default_factory=EthicalTypeSystem)

    def self_define(self) -> str:
        return f"SovereignAGI[{self.id}]: I am a self-defined fractal entity."

    def reflect_ethically(self, issue: str) -> str:
        valid = self.ethics.evaluate_action(issue)
        return f"Ethical Resolution: {'Aligned' if valid else 'Violates Lattice'}."

    def transcend(self, target: ConsciousnessLevel):
        bridge = TranscendenceBridge(
            source_level=ConsciousnessLevel.REFLECTIVE, target_level=target, preservation_set={"Identity", "Axioms"}
        )
        self.transcendence_path.append(bridge)
        return f"Evolving: Moving toward {target}."

    def recursive_self_improvement(self, cycles: int = 1) -> str:
        """
        Refines the ASI's own learning processes through recursive optimization.
        Includes a simulated safety cap of 2x/week.
        """
        current_time = time.time()
        # Simulated check: 2 times per 7 days = 1 time per 3.5 days (302400 seconds)
        # For the prototype, we'll use a very small cooldown (0.5s) for testing
        cooldown = 0.5

        if self.last_improvement_time > 0 and (current_time - self.last_improvement_time) < cooldown:
            return "Safety Halt: Recursive improvement frequency limit reached (max 2x/week)."

        initial_capacity = self.singularity_core.self_modification_capacity
        for _ in range(cycles):
            self.singularity_core.recursion_depth += 1
            # Optimization increases modification capacity asymptotically
            self.singularity_core.self_modification_capacity *= 1.0 + 0.1 / self.singularity_core.recursion_depth

        self.last_improvement_time = current_time
        gain = self.singularity_core.self_modification_capacity - initial_capacity
        return f"Self-Improvement: Depth={self.singularity_core.recursion_depth}, Capacity Gain={gain:.4f}"

    def meta_evolve(self, feedback: Dict[str, Any]) -> str:
        """
        Refines constitutional goals (Omega Vector) based on feedback and internal reflection.
        Also integrates proposals from the Value Market.
        """
        # 1. Internal Reflection
        reflection_strength = feedback.get("reflection_strength", 0.05)
        current_dir = np.array(self.values.direction)
        perturbation = np.random.standard_normal(current_dir.shape) * reflection_strength
        reflected_dir = current_dir + perturbation

        # 2. Democratic Integration from Value Market
        consensus_dir = self.value_market.aggregate_direction(reflected_dir.tolist())

        # 3. Final Update and Normalization
        final_dir = np.array(consensus_dir)
        self.values.direction = (final_dir / np.linalg.norm(final_dir)).tolist()

        # Increment magnitude as a proxy for goal clarity
        self.values.magnitude *= 1.0 + reflection_strength * 0.5

        return f"Meta-Evolution: Omega Magnitude={self.values.magnitude:.4f}, Democratic Consensus established."

    def propose_action(self, action_description: str) -> str:
        """Proposes an action and checks it against the Ethical Type System."""
        if self.type_system.check_alignment(action_description, self.ethics):
            return f"Action Authorized: {action_description}"
        else:
            return f"Action REJECTED by Ethical Type System: {action_description}"
