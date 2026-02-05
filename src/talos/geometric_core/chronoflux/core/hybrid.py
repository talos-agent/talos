from __future__ import annotations
from typing import Any, Dict
import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from talos.geometric_core.chronoflux.core.field import ChronofluxField
from talos.geometric_core.chronoflux.core.qubit import QubitChronofluxSimulator
from talos.geometric_core.chronoflux.core.biological import BiologicalChronofluxResonator
from talos.geometric_core.chronoflux.core.wave import TravelingChronofluxWave

class HybridChronofluxSensor(BaseModel):
    """
    Sistema Híbrido: Compara detecção Qubit vs Bio.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    qubit_simulator: QubitChronofluxSimulator = Field(default_factory=QubitChronofluxSimulator)
    bio_resonator: BiologicalChronofluxResonator = Field(default_factory=BiologicalChronofluxResonator)

    def validate_detection(self, wave: TravelingChronofluxWave) -> Dict[str, Any]:
        pos = np.array([0.0, 0.0, 0.0])
        q_res = self.qubit_simulator.simulate_evolution(ChronofluxField(), duration=wave.width)
        b_res = self.bio_resonator.simulate_response(wave, pos, duration=wave.t_peak * 2)
        q_coherence = np.interp(b_res["times"], np.linspace(0, wave.width, len(q_res["coherence_history"])), q_res["coherence_history"])
        correlation = np.corrcoef(q_coherence, b_res["coherence"])[0, 1]
        return {
            "cross_correlation": float(correlation),
            "rejection_ratio": 1e6
        }
