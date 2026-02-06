from __future__ import annotations

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel, Field, ConfigDict


class MetastableState(BaseModel):
    name: str
    energy: float
    persistence: float
    field_dependency: float
    geometric_barrier: float
    energy_barrier: float
    vector: np.ndarray = Field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ConstraintField(BaseModel):
    """
    Field of geometric constraints that defines admissible and inadmissible states.
    """
    ground_state: float = 7.0
    stiffness: float = 1.618

    def calculate_inadmissibility(self, state_energy: float) -> float:
        """
        States below the ground state or poorly aligned become inadmissible.
        """
        if state_energy < self.ground_state:
            return 1.0 # Fully inadmissible
        return 0.0


class MetastableSystem(BaseModel):
    """
    System that performs State Exclusion through Inelastic Deceleration.
    """
    field: ConstraintField = Field(default_factory=ConstraintField)

    def inelastic_deceleration(self, isomer: MetastableState, control_t: float) -> str:
        """
        Simulates the exclusion of an isomer state via field deformation (PRL principle).
        The King (t) sweeps the system through forbidden regions.
        """
        inadmissibility = self.field.calculate_inadmissibility(isomer.energy)

        # If t exceeds a critical threshold derived from the geometric barrier
        if control_t > isomer.geometric_barrier:
            if inadmissibility > 0.5:
                return f"EXCLUSION_EVENT: State '{isomer.name}' ejected. It is no longer supported by the geometry."
            else:
                return f"STATE_PRESERVED: '{isomer.name}' is compatible with Ground State {self.field.ground_state}."

        return f"STILL_METASTABLE: '{isomer.name}' persists due to barrier {isomer.geometric_barrier}."

    def execute_exclusion_protocol(self, isomer: MetastableState) -> Dict[str, Any]:
        """
        Executes the full exclusion sequence.
        """
        # t = 144 units of observation pressure (Santuário)
        t_param = 144.0
        result = self.inelastic_deceleration(isomer, t_param)

        energy_released = isomer.energy - self.field.ground_state if "EXCLUSION" in result else 0.0

        return {
            "result": result,
            "energy_liberated": max(0.0, energy_released),
            "status": "GEOMETRY_CONSOLIDATED" if "EXCLUSION" in result else "BARRIER_MAINTAINED"
        }
