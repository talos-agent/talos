from __future__ import annotations

from typing import List

import numpy as np
from pydantic import BaseModel, ConfigDict


class PrometheusTrainingProtocol(BaseModel):
    """
    Stability controls for shell-native learning.
    Interior is measures-theoretic darkness; learning happens on the boundary.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    clipping_threshold: float = 1.0
    learning_rate: float = 0.01
    shell_radius: float = 1.0

    def apply_shell_clipping(self, gradients: np.ndarray) -> np.ndarray:
        """
        Clips gradients based on hypersphere curvature limits.
        """
        norm = np.linalg.norm(gradients)
        if norm > self.clipping_threshold:
            return gradients * (self.clipping_threshold / norm)
        return gradients

    def update_shell_weights(self, weights: np.ndarray, gradients: np.ndarray) -> np.ndarray:
        """
        Performs a learning step, ensuring weights remain anchored on the typicality shell.
        """
        clipped_grads = self.apply_shell_clipping(gradients)
        new_weights = weights - self.learning_rate * clipped_grads

        # Re-project to Shell (Accept the law)
        norm = np.linalg.norm(new_weights)
        return new_weights * (self.shell_radius / (norm + 1e-9))

    def detect_mode_collapse(self, weights_history: List[np.ndarray]) -> bool:
        """
        Detects if learning has collapsed into a single point (losing shell diversity).
        """
        if len(weights_history) < 2:
            return False

        # Diversity check: variances of angular positions
        stacked = np.stack(weights_history)
        variances = np.var(stacked, axis=0)
        return float(np.mean(variances)) < 1e-6
