from __future__ import annotations

from typing import Any, Dict

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class MoireLattice(BaseModel):
    """
    Models a Moiré interference pattern between two twisted manifolds.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    twist_angle: float = 1.1 * (np.pi / 180.0)  # 1.1 degrees (Magic Angle for Graphene)
    dimension: int = 11

    def generate_rotation_matrix(self, angle: float) -> np.ndarray:
        """Simple rotation in a 2D subspace of the high-D manifold."""
        rot = np.eye(self.dimension)
        c, s = np.cos(angle), np.sin(angle)
        # Apply rotation to the first two dimensions as a proxy for the complex twist
        rot[0, 0] = c
        rot[0, 1] = -s
        rot[1, 0] = s
        rot[1, 1] = c
        return rot

    def compute_interference(self, rep_a: np.ndarray, rep_b: np.ndarray) -> np.ndarray:
        """
        Computes the interference pattern (Moiré) between two representations.
        In Moire superlattices, this creates areas of constructive/destructive interference.
        """
        # Constructive interference where they align
        return (rep_a + rep_b) / 2.0


class TwistedAttention(BaseModel):
    """
    Implements 'Twisted Attention' inspired by Moire Physics.
    Uses twist angles to generate high-order emergent representations.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    dimension: int = 11
    magic_angle: float = 1.1 * (np.pi / 180.0)
    lattice: MoireLattice = Field(default_factory=lambda: MoireLattice(dimension=11))

    def forward(self, x: np.ndarray) -> Dict[str, Any]:
        """
        Forward pass for Twisted Attention.
        """
        # 1. Generate Twisted Representations
        rot_a = self.lattice.generate_rotation_matrix(self.magic_angle / 2.0)
        rot_b = self.lattice.generate_rotation_matrix(-self.magic_angle / 2.0)

        rep_a = np.dot(x, rot_a.T)
        rep_b = np.dot(x, rot_b.T)

        # 2. Compute Moiré Interference
        moire_rep = self.lattice.compute_interference(rep_a, rep_b)

        # 3. Calculate Attention Weights modulated by Moiré pattern
        # Higher interference = higher attention weight (Constructive binding)
        sim = np.matmul(moire_rep, x.T)

        # Complexity reduction simulation: only attend to high-interference regions
        threshold = np.percentile(sim, 70)
        mask = sim > threshold

        weights = np.exp(sim - np.max(sim, axis=-1, keepdims=True))
        weights = weights * mask
        weights /= np.sum(weights, axis=-1, keepdims=True) + 1e-9

        output = np.dot(weights, x)

        return {
            "output": output,
            "twist_angle_deg": float(np.degrees(self.magic_angle)),
            "moire_coherence": float(np.mean(np.linalg.norm(moire_rep, axis=-1))),
            "active_domains": int(np.sum(mask)),
            "complexity_ratio": float(np.sum(mask) / (x.shape[0] * x.shape[0])),
            "is_twisted": True,
        }
