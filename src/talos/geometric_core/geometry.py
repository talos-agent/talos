from __future__ import annotations

from typing import Any

import jax
import jax.numpy as jnp
from pydantic import BaseModel, ConfigDict


class GeometricMotor(BaseModel):
    """
    Geometric optimization engine.
    Implements natural gradient descent on the parameter manifold.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    learning_rate: float = 0.01

    def step(self, params: jnp.ndarray, grads: jnp.ndarray, fisher: float, state: Any) -> jnp.ndarray:
        """
        Performs a single step of geometric optimization.
        Uses fisher information and intuition-state anxiety to modulate step size.
        """
        # Natural Gradient = G^-1 * grad
        # Modulate by anxiety (higher anxiety = smaller steps to avoid singularity)
        anxiety_modulation = 1.0 / (1.0 + state.anxiety_level * 0.1)

        effective_lr = self.learning_rate * anxiety_modulation

        # Precondition with scalar Fisher (simplified)
        preconditioned_grad = grads / (fisher + 1e-8)

        return params - effective_lr * preconditioned_grad
