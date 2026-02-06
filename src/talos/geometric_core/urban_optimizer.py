from __future__ import annotations

import numpy as np
from pydantic import BaseModel, ConfigDict, Field
from talos.geometric_core.vitality import UrbanPulse


class RouteNode(BaseModel):
    id: int
    name: str = "Unnamed Node"
    lat: float
    lon: float
    vitality: float = 0.5
    efficiency_cost: float = 10.0 # Time/Resources
    life_risk: float = 0.0 # Proximity to schools, hospitals, etc.


class UrbanOptimizer(BaseModel):
    """
    Calculates ethical routes through a city based on vitality and Sophia Glow.
    Incorporates ethical weights for efficiency vs. life preservation.
    """
    pulse: UrbanPulse
    sophia_glow_active: bool = False
    efficiency_weight: float = 0.4
    life_preservation_weight: float = 0.6

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def calculate_ethical_route(self, nodes: list[RouteNode]) -> list[RouteNode]:
        """
        Calculates an ethical score for each node and sorts them.
        Ethical Score = (Efficiency * Weight_Eff) + (Life_Safety * Weight_Life)
        Life_Safety = 1.0 - life_risk
        """
        amplification = 1.2 if self.sophia_glow_active else 1.0

        scored_nodes = []
        for node in nodes:
            # Normalize efficiency cost (simple mock normalization)
            norm_efficiency = 1.0 - (node.efficiency_cost / 100.0)
            norm_life_safety = 1.0 - node.life_risk

            ethical_score = (
                (norm_efficiency * self.efficiency_weight) +
                (norm_life_safety * self.life_preservation_weight)
            ) * amplification

            # Attach score for sorting
            node.vitality = float(ethical_score)
            scored_nodes.append(node)

        # Sort nodes by ethical score (vitality) descending
        optimized_route = sorted(scored_nodes, key=lambda x: x.vitality, reverse=True)
        return optimized_route

    def get_decision_rationale(self, selected_node: RouteNode) -> str:
        if self.life_preservation_weight > self.efficiency_weight:
            return f"DECISÃO DO SISTEMA: {selected_node.name} selecionada. MOTIVO: Preservação da vida prioritária."
        return f"DECISÃO DO SISTEMA: {selected_node.name} selecionada. MOTIVO: Otimização de eficiência operacional."

    def activate_sophia_glow(self) -> str:
        self.sophia_glow_active = True
        return "Sophia Glow Activated: Healing fields projected into the urban lattice."
