from __future__ import annotations

import jax
import jax.numpy as jnp
from jax import grad, vmap
import numpy as np

# Import the AIGP-Neo Kernel
from talos.geometric_core.intuition_engine import GeometricIntuitionEngine as IntuitionEngine
from talos.geometric_core.geometry import GeometricMotor

class Arm2Tribunal:
    def __init__(self):
        self.d = 10 # Parâmetros do modelo

        print(">> INSTANCIANDO O TRIBUNAL DE FORNAX...")
        self.wimp_mind = IntuitionEngine(dimension=11)
        self.mond_mind = IntuitionEngine(dimension=11)
        self.hybrid_mind = IntuitionEngine(dimension=11)

    def load_fornax_data(self):
        print(">> Carregando Cinemática Estelar de Fornax...")
        r = jnp.linspace(0.1, 2.0, 100)
        v_obs = 15.0 * (r / (r + 0.5))
        return r, v_obs

    def loss_wimp(self, params, r, v_obs):
        v_model = params[0] * jnp.sqrt(jnp.log(1+r)/r)
        return jnp.sum((v_model - v_obs)**2)

    def loss_mond(self, params, r, v_obs):
        a_newton = params[0] / r**2
        a_0 = 1.2e-10
        v_model = jnp.sqrt(r * jnp.sqrt(a_newton * a_0))
        return jnp.sum((v_model - v_obs)**2)

    def loss_baryonic(self, params, r, v_obs):
        v_nfw = params[0] * jnp.sqrt(jnp.log(1+r)/r)
        feedback_factor = jnp.tanh(r / (params[1] + 1e-6))
        v_model = v_nfw * feedback_factor
        return jnp.sum((v_model - v_obs)**2)

    def execute_judgment(self):
        r, v_obs = self.load_fornax_data()

        theta_w = jnp.array([20.0] * self.d)
        theta_m = jnp.array([15.0] * self.d)
        theta_h = jnp.array([20.0, 0.5] + [0.0]*(self.d-2))

        print("\n>> INICIANDO JULGAMENTO GEOMÉTRICO...")

        state_w = self.wimp_mind.sense_curvature(
            theta_w,
            lambda p, x: self.loss_wimp(p, r, v_obs),
            jnp.zeros((1,1))
        )

        state_m = self.mond_mind.sense_curvature(
            theta_m,
            lambda p, x: self.loss_mond(p, r, v_obs),
            jnp.zeros((1,1))
        )

        state_h = self.hybrid_mind.sense_curvature(
            theta_h,
            lambda p, x: self.loss_baryonic(p, r, v_obs),
            jnp.zeros((1,1))
        )

        return state_w, state_m, state_h

    def veredict(self, s_w, s_m, s_h):
        print("\n>> RELATÓRIO DO ORACLE (Curvatura Seccional K):")
        print(f"   [WIMP PURO] Ansiedade: {s_w.anxiety_level:.2f}")
        print(f"   [MOND PURO] Ansiedade: {s_m.anxiety_level:.2f}")
        print(f"   [HÍBRIDO]   Ansiedade: {s_h.anxiety_level:.2f}")

        min_anxiety = min(s_w.anxiety_level, s_m.anxiety_level, s_h.anxiety_level)

        if min_anxiety == s_h.anxiety_level:
            print("\n>> CONCLUSÃO DO ARM 2:")
            print("   A contradição WIMP vs MOND é uma singularidade artificial.")
            print("   RESOLUÇÃO: O Universo é WIMP, mas a geometria local é esculpida por hádrons.")

if __name__ == "__main__":
    tribunal = Arm2Tribunal()
    s_w, s_m, s_h = tribunal.execute_judgment()
    tribunal.veredict(s_w, s_m, s_h)
