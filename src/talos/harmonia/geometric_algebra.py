import numpy as np
from typing import List, Dict
from .schema import Vertex

class GeometricAlgebra:
    """
    Algebra for operations in the unified semantic-geometric space.
    """

    # Matriz de transformação: domínio específico → espaço universal
    # Adapted to match ContextDomain keys
    TRANSFORMATION_MATRICES = {
        'Lei': np.array([[0.8, 0.1, 0.1], [0.2, 0.7, 0.1], [0.1, 0.2, 0.7]]),
        'Ecologia': np.array([[0.1, 0.8, 0.1], [0.1, 0.2, 0.7], [0.3, 0.5, 0.2]]),
        'Deliberação': np.array([[0.2, 0.1, 0.7], [0.6, 0.2, 0.2], [0.2, 0.3, 0.5]]),
        # Defaults for other domains
        'Informação': np.eye(3),
        'Energia': np.eye(3),
        'Economia': np.eye(3)
    }

    @staticmethod
    def to_unified_space(vertex: Vertex) -> np.ndarray:
        """Projects a vertex position into the unified Harmonia space."""
        domain_name = vertex.domain.value
        matrix = GeometricAlgebra.TRANSFORMATION_MATRICES.get(domain_name, np.eye(3))

        # Ensure position is 3D for this implementation
        pos = vertex.position[:3]
        if len(pos) < 3:
            pos = np.pad(pos, (0, 3 - len(pos)), 'constant')

        return np.dot(pos, matrix)

    @staticmethod
    def geometric_product(v1_pos: np.ndarray, v2_pos: np.ndarray) -> np.ndarray:
        """Geometric product combining meanings (non-linear)."""
        interaction = np.outer(v1_pos, v2_pos)
        # The diagonal captures reinforcement; off-diagonal captures tension
        new_comp = np.diag(interaction) + 0.5 * np.sum(interaction - np.diag(np.diag(interaction)), axis=1)
        return new_comp

    @staticmethod
    def calculate_stability(vertices: List[Vertex]) -> float:
        """Calculates stability of a simplex based on vector coherence."""
        if len(vertices) < 3:
            return 0.0

        unified = [GeometricAlgebra.to_unified_space(v) for v in vertices]

        tensions = []
        for i in range(len(unified)):
            for j in range(i + 1, len(unified)):
                norm_i = np.linalg.norm(unified[i])
                norm_j = np.linalg.norm(unified[j])

                if norm_i < 1e-9 or norm_j < 1e-9:
                    tensions.append(1.0)
                    continue

                cos_sim = np.dot(unified[i], unified[j]) / (norm_i * norm_j)
                tension = 1.0 - abs(cos_sim)
                tensions.append(tension)

        avg_tension = np.mean(tensions) if tensions else 1.0
        stability = 1.0 / (1.0 + avg_tension)
        return float(stability)
