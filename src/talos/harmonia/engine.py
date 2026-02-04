from __future__ import annotations

from typing import Any, Dict, List, Optional

from .factory import create_forest_simplex
from .semantic_network import UnifiedSemanticNetwork


class HarmoniaEngine:
    """
    High-level engine to interface with the HARMONIA 2.0 system.
    """

    def __init__(self):
        # Initialize with the default forest simplex
        self.network, self.initial_simplex = create_forest_simplex()

    def analyze_resonance(self, start_concept_id: str, strength: float = 1.0) -> Dict[str, Any]:
        """
        Analyzes how an effect at one concept resonates through the network.
        """
        if start_concept_id not in self.network.vertices:
            return {"error": f"Concept {start_concept_id} not found."}

        effects = self.network.propagate_effect(start_concept_id, strength)

        results = []
        for cid, weight in effects.items():
            vertex = self.network.vertices[cid]
            results.append({"id": cid, "name": vertex.name, "domain": vertex.domain.value, "resonance": weight})

        return {
            "origin": self.network.vertices[start_concept_id].name,
            "resonance_field": sorted(results, key=lambda x: x["resonance"], reverse=True),
            "global_coherence": self.initial_simplex.stability,
        }
