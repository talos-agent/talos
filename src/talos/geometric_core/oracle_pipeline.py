from __future__ import annotations

from typing import Dict

import jax
import jax.numpy as jnp
import numpy as np

from talos.geometric_core.oracle import FeasibleTwoTierOracle


class OracleValidationPipeline:
    """
    Validation Pipeline for Geometric Singularity Detection.
    Tests detection accuracy on synthetic loss landscapes.
    """

    def __init__(self, param_dim: int = 10):
        self.d = param_dim
        self.oracle = FeasibleTwoTierOracle(param_dim=param_dim, n_bootstrap=20, n_geodesic_samples=10)

    def run_validation(self, n_trials: int = 100) -> Dict[str, float]:
        results = []

        for i in range(n_trials):
            key = jax.random.PRNGKey(i)
            batch = jax.random.normal(key, (32, 1))

            # Select scenario
            scenario = i % 3
            if scenario == 0:
                # Metric Singularity
                def loss(p, x):
                    return jnp.mean((x - p[0] * p[1]) ** 2) + 0.1 * jnp.sum(p**2)

                params = jnp.zeros(self.d)
                expected = "STATISTICAL_SINGULARITY_NON_IDENTIFIABLE"
            elif scenario == 1:
                # Curvature Blowup
                def loss(p, x):
                    return jnp.mean((x - p[0]) ** 2) + 0.01 / (jnp.sum(p[:2] ** 2) + 1e-15)

                params = jnp.array([1e-6, 1e-6] + [0.0] * (self.d - 2))
                expected = "PHASE_TRANSITION_BLOWUP"
            else:
                # Regular
                def loss(p, x):
                    return jnp.mean((x - p[0]) ** 2) + jnp.sum(p**2)

                params = jnp.ones(self.d)
                expected = "REGULAR"

            kfac_state = {"cond_number": 1e8, "top_variance": 0.9}
            analysis = self.oracle.analyze(params, kfac_state, batch, loss)

            if analysis["tier"] == 2:
                sig_type = analysis["signature"].singularity_type
                results.append(1.0 if sig_type == expected else 0.0)
            else:
                results.append(1.0 if expected == "REGULAR" else 0.0)

        accuracy = np.mean(results)
        return {"accuracy": accuracy, "trials": float(n_trials)}


if __name__ == "__main__":
    pipeline = OracleValidationPipeline()
    report = pipeline.run_validation()
    print(f"Validation Report: {report}")
