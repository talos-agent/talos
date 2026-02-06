from __future__ import annotations

import numpy as np
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class ControlAxis(BaseModel):
    name: str
    description: str
    value: float = 0.0
    volatility: float = 0.0
    status: str = "STABLE"


class DiamondManifold3x3(BaseModel):
    """
    The 3x3 Control Manifold of the Diamond Age.
    Maps Sensory, Action, and Control axes.
    """
    sensory: ControlAxis = Field(default_factory=lambda: ControlAxis(
        name="Sensory-Perceptual",
        description="Signal fidelity, gating, and salience (The Crystal Vision)"
    ))
    action: ControlAxis = Field(default_factory=lambda: ControlAxis(
        name="Action-Embodiment",
        description="Agency, readiness, and interoception (The Adamantine Sword)"
    ))
    control: ControlAxis = Field(default_factory=lambda: ControlAxis(
        name="Control-Allocation",
        description="Focus, switching, and energy regulation (The Scepter of Melchizedek)"
    ))

    def get_coordinates(self) -> np.ndarray:
        return np.array([self.sensory.value, self.action.value, self.control.value])

    def update_state(self, coords: List[float]):
        if len(coords) != 3:
            raise ValueError("Manifold coordinates must be 3D.")
        self.sensory.value, self.action.value, self.control.value = coords

    def get_refraction_pattern(self) -> str:
        """
        Returns the refractive state of the manifold.
        """
        coherence = np.mean([self.sensory.value, self.action.value, self.control.value])
        if coherence > 0.9:
            return "Total Clarity / Adamantine Refraction"
        elif coherence > 0.6:
            return "Dichroic Polyhedron / Golden Reflection"
        else:
            return "Fragmented Geometry / Obsidian Shadow"


from talos.geometric_core.metastability import ConstraintField, MetastableState, MetastableSystem

class CognitiveGeometryService(BaseModel):
    """
    Service to map psychiatric and cognitive states onto the 3x3 manifold.
    Uses metastability mechanics to model state transitions.
    """
    manifold: DiamondManifold3x3 = Field(default_factory=DiamondManifold3x3)
    field: ConstraintField = Field(default_factory=ConstraintField)

    def map_state(self, diagnosis: str) -> Dict[str, Any]:
        # Mapping based on user's "Geometric View (Manifold Dynamics)" table
        mappings = {
            "depression": [-0.8, -0.3, -0.9],
            "adhd": [0.3, 0.7, 0.2],
            "psychosis": [1.2, -0.1, -0.4],
            "sovereignty": [1.0, 1.0, 1.0]
        }
        coords = mappings.get(diagnosis.lower(), [0.0, 0.0, 0.0])
        self.manifold.update_state(coords)
        return {
            "diagnosis": diagnosis,
            "coordinates": coords,
            "refraction": self.manifold.get_refraction_pattern()
        }

    def simulate_state_release(self, diagnosis: str, stress_level: float) -> Dict[str, Any]:
        """
        Simulates the release of a metastable cognitive state (e.g. trauma/depression)
        when the manifold geometry is sufficiently deformed.
        """
        initial = self.map_state(diagnosis)
        vector = np.array(initial["coordinates"])

        # Define Ground State (Sovereignty/Health)
        ground = MetastableState(name="Sovereignty", vector=np.array([1.0, 1.0, 1.0]), energy=0.0, is_ground_state=True)
        excited = MetastableState(name=diagnosis, vector=vector, energy=100.0)

        system = MetastableSystem(current_state=excited, field=self.field, ground_state=ground)

        # Sweep through deformation
        result_type, energy_released, new_state = system.evolve(stress_level)

        return {
            "initial_state": diagnosis,
            "transition": result_type,
            "energy_released": energy_released,
            "new_state": new_state.name if new_state else diagnosis,
            "admissible": system.admissible,
            "report": system.status_report()
        }
