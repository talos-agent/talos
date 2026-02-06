from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class ShellExpert(BaseModel):
    """
    An expert module identified by its resonant mode on the shell.
    """

    id: str
    resonance_signature: np.ndarray = Field(
        default_factory=lambda: np.random.standard_normal(11)
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ShellRouter(BaseModel):
    """
    MoE Router that uses harmonic resonance (interference patterns) on the shell.
    The interior is ghost; routing happens on the boundary.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    experts: List[ShellExpert] = Field(default_factory=list)
    top_k: int = 2
    dimension: int = 11

    def route(self, token_embeddings: np.ndarray) -> Dict[str, Any]:
        """
        Routes tokens to experts based on shell-harmonic resonance.
        token_embeddings: (batch_size, dimension)
        """
        if not self.experts:
            return {"error": "No experts registered"}

        # Normalize expert signatures to shell surface
        expert_sigs = np.array(
            [
                e.resonance_signature / (np.linalg.norm(e.resonance_signature) + 1e-9)
                for e in self.experts
            ]
        )

        # Normalize tokens to shell surface
        tokens_shell = token_embeddings / (
            np.linalg.norm(token_embeddings, axis=-1, keepdims=True) + 1e-9
        )

        # Resonance (interference) = token_shell dot expert_signature
        resonance = np.matmul(tokens_shell, expert_sigs.T)

        # Top-K selection
        indices = np.argsort(resonance, axis=-1)[:, -self.top_k :]
        scores = np.take_along_axis(resonance, indices, axis=-1)

        # Softmax normalization for mixture weights
        exp_scores = np.exp(scores - np.max(scores, axis=-1, keepdims=True))
        probs = exp_scores / (np.sum(exp_scores, axis=-1, keepdims=True) + 1e-9)

        return {
            "expert_indices": indices.tolist(),
            "mixture_probs": probs.tolist(),
            "resonance_field": resonance.tolist(),
            "max_resonance": float(np.max(resonance)),
        }
