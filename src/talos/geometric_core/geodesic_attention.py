from __future__ import annotations

from enum import Enum
from typing import Any, Dict

import numpy as np
from pydantic import BaseModel, ConfigDict


class CurvatureEstimator(str, Enum):
    LAPLACIAN = "laplacian"
    ENTROPY = "entropy"
    GRADIENT = "gradient"


class GeodesicAttention(BaseModel):
    """
    Implements Geodesic Attention with adaptive curvature.
    Reduces complexity from O(n^2) to O(n log n) simulation.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    dimension: int = 11
    base_k: int = 32
    alpha: float = 0.5
    max_k: int = 256
    shell_radius: float = 1.0
    estimator: CurvatureEstimator = CurvatureEstimator.LAPLACIAN

    def project_to_shell(self, x: np.ndarray) -> np.ndarray:
        """
        Normalizes vectors to the hypersphere surface (The Shell).
        """
        norm = np.linalg.norm(x, axis=-1, keepdims=True)
        return x / (norm + 1e-9) * self.shell_radius

    def estimate_curvature(self, sim: np.ndarray, x: np.ndarray) -> np.ndarray:
        """
        Estimates the local curvature of the semantic manifold.
        """
        if self.estimator == CurvatureEstimator.LAPLACIAN:
            # L = D - A
            degree = np.sum(sim, axis=-1, keepdims=True)
            laplacian = degree - sim
            return np.sum(np.abs(laplacian), axis=-1)
        elif self.estimator == CurvatureEstimator.ENTROPY:
            # High entropy = low curvature
            exp_sim = np.exp(sim - np.max(sim, axis=-1, keepdims=True))
            probs = exp_sim / (np.sum(exp_sim, axis=-1, keepdims=True) + 1e-9)
            entropy = -np.sum(probs * np.log(probs + 1e-9), axis=-1)
            return (np.max(entropy) - entropy) / (np.max(entropy) + 1e-9)
        else:  # Gradient
            grad_x = np.diff(x, axis=0, prepend=x[0:1])
            return np.linalg.norm(grad_x, axis=-1)

    def compute_adaptive_k(self, curvature: np.ndarray) -> np.ndarray:
        """
        Computes adaptive K based on curvature: k_i = base_k * (1 + alpha * c_i).
        """
        # Normalize curvature for scaling
        c_norm = curvature / (np.max(curvature) + 1e-9)
        k = self.base_k * (1.0 + self.alpha * c_norm)
        return np.clip(k, self.base_k, self.max_k).astype(int)

    def forward(self, x: np.ndarray) -> Dict[str, Any]:
        """
        Forward pass with geodesic sparse attention.
        """
        seq_len, dim = x.shape

        # Project to shell
        q_shell = self.project_to_shell(x)
        k_shell = self.project_to_shell(x)
        v = x.copy()

        # Geodesic similarity: product is cos(theta)
        sim = np.matmul(q_shell, k_shell.T)

        # Curvature-adaptive sparsity
        curvature = self.estimate_curvature(sim, x)
        k_adaptive = self.compute_adaptive_k(curvature)

        output = np.zeros_like(x)

        # Sparse top-k attention loop (simulation of efficient kernel)
        for i in range(seq_len):
            ki = min(k_adaptive[i], seq_len)
            # Efficiently find top-ki neighbors
            idx = np.argpartition(sim[i], -ki)[-ki:]

            # Masked softmax
            weights = np.exp(sim[i, idx] - np.max(sim[i, idx]))
            weights /= np.sum(weights)

            output[i] = np.dot(weights, v[idx])

        # Actual keys attended
        actual_k = np.minimum(k_adaptive, seq_len)

        return {
            "output": output,
            "curvature_mean": float(np.mean(curvature)),
            "k_mean": float(np.mean(actual_k)),
            "complexity_ratio": float(np.mean(actual_k) / seq_len),
            "is_geodesic": True,
        }
