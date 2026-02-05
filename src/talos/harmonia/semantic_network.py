from __future__ import annotations

from typing import Dict, List, Set, Tuple

from .geometric_algebra import GeometricAlgebra
from .schema import ContextDomain, Edge, Simplex, Vertex


class UnifiedSemanticNetwork:
    """
    Network connecting information, law, ecology, energy, economy, and deliberation.
    Minimal implementation without external graph libraries.
    """

    def __init__(self):
        self.vertices: Dict[str, Vertex] = {}
        self.edges: List[Edge] = []
        self.simplexes: Dict[str, Simplex] = {}
        self.adjacency: Dict[str, List[Edge]] = {}

    def add_concept(self, vertex: Vertex):
        self.vertices[vertex.id] = vertex
        if vertex.id not in self.adjacency:
            self.adjacency[vertex.id] = []

    def add_relation(self, source_id: str, target_id: str, relation_type: str, weight: float = 1.0):
        if source_id not in self.vertices or target_id not in self.vertices:
            raise ValueError("Source or target vertex not found")

        source = self.vertices[source_id]
        target = self.vertices[target_id]

        transformation = self._get_transformation_rule(source.domain, target.domain)

        edge = Edge(
            source=source_id,
            target=target_id,
            relation_type=relation_type,
            weight=weight,
            transformation=transformation,
        )
        self.edges.append(edge)
        self.adjacency[source_id].append(edge)

    def _get_transformation_rule(self, source_domain: ContextDomain, target_domain: ContextDomain) -> str:
        rules = {
            (ContextDomain.LAW, ContextDomain.ECONOMY): "regulates_access_to",
            (ContextDomain.ECONOMY, ContextDomain.ENERGY): "enables_funding_for",
            (ContextDomain.INFORMATION, ContextDomain.DELIBERATION): "informs_decisions_in",
            (ContextDomain.ECOLOGY, ContextDomain.LAW): "justifies_legislation_for",
        }
        return rules.get((source_domain, target_domain), "direct")

    def form_simplex(self, id: str, name: str, vertex_ids: List[str], semantic_type: str) -> Simplex:
        verts = [self.vertices[vid] for vid in vertex_ids]
        stability = GeometricAlgebra.calculate_stability(verts)

        simplex = Simplex(id=id, name=name, vertices=vertex_ids, stability=stability, semantic_type=semantic_type)
        self.simplexes[id] = simplex
        return simplex

    def propagate_effect(self, start_id: str, effect_strength: float = 1.0) -> Dict[str, float]:
        visited: Set[str] = set()
        queue: List[Tuple[str, float]] = [(start_id, effect_strength)]
        effects: Dict[str, float] = {}

        while queue:
            current, strength = queue.pop(0)
            if current in visited or strength < 0.1:
                continue

            visited.add(current)
            effects[current] = effects.get(current, 0.0) + strength

            for edge in self.adjacency.get(current, []):
                neighbor = edge.target
                weight = edge.weight
                trans = edge.transformation

                if trans == "direct":
                    new_strength = strength * weight * 0.8
                elif trans == "regulates_access_to":
                    new_strength = strength * weight * 1.2
                else:
                    new_strength = strength * weight * 0.6

                queue.append((neighbor, new_strength))

        return effects
