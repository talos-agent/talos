from __future__ import annotations

import jax
import jax.numpy as jnp
from jax import grad, vmap
import numpy as np

# Import the AIGP-Neo Kernel
from talos.geometric_core.intuition_engine import GeometricIntuitionEngine as IntuitionEngine

class Arm3Navigator:
    def __init__(self):
        self.d = 10
        print(">> INICIALIZANDO NAVEGADOR DE OBSERVAÇÃO...")
        self.oracle = IntuitionEngine(dimension=11)

    def sensitivity_map(self, params, r_grid):
        v_pure = params[0] * jnp.sqrt(jnp.log(1+r_grid)/r_grid)
        feedback_scale = params[1]
        v_hybrid = v_pure * jnp.tanh(r_grid / (feedback_scale + 1e-6))
        signature = jnp.abs(v_pure - v_hybrid)
        return signature

    def target_acquisition(self):
        print(">> CALCULANDO VETORES DE APONTAMENTO ÓTIMO...")
        r_grid = jnp.linspace(0.01, 5.0, 500)
        params = jnp.array([20.0, 0.5] + [0.0]*(self.d-2))

        signature = self.sensitivity_map(params, r_grid)
        peak_idx = jnp.argmax(signature)
        r_optimal = r_grid[peak_idx]
        max_sig = signature[peak_idx]

        mock_obs = signature[peak_idx] + jax.random.normal(jax.random.PRNGKey(0), shape=(1,))*0.1

        intuition_state = self.oracle.sense_curvature(
            params,
            lambda p, x: (self.sensitivity_map(p, r_optimal) - x)**2,
            jnp.array([[mock_obs]])
        )

        return r_optimal, max_sig, intuition_state

    def generate_observing_proposal(self, r_opt, sig, state):
        print("\n>> GERANDO PROPOSTA DE OBSERVAÇÃO (JWST / EUCLID / ROMAN)...")
        print("---------------------------------------------------------------")
        print(f"ALVO PRIMÁRIO:  Região Central de Galáxias Anãs Ultra-Fracas")
        print(f"RAIO ÓTIMO:     r = {r_opt:.3f} kpc")
        print(f"SINAL ESPERADO: {sig:.2f} km/s")
        print(f"CONFIANÇA AIGP: {state.confidence*100:.1f}%")
        print("---------------------------------------------------------------")

        if r_opt < 1.0:
            print(">> RECOMENDAÇÃO DE INSTRUMENTO: NIRSpec (JWST)")
        else:
            print(">> RECOMENDAÇÃO DE INSTRUMENTO: VIS/NISP (Euclid)")

if __name__ == "__main__":
    nav = Arm3Navigator()
    r_opt, sig, state = nav.target_acquisition()
    nav.generate_observing_proposal(r_opt, sig, state)
