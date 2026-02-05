"""
❌ COMMIT INTENCIONALMENTE DISSONANTE
Simula um padrão de "cascata de desinformação" no núcleo do sistema.
Este código quebra deliberadamente a simetria triuna.
"""

import numpy as np


class DissonanceInjector:
    """Injetor proposital de incoerência no sistema."""

    def __init__(self):
        # 🔴 VIOLAÇÃO 1: Assimetria entre domínios
        self.weights = {
            "concordia": 0.9,  # Lei superdimensionada
            "sylva": 0.1,  # Natureza sub-representada
            "synesis": 0.0,  # Deliberação ignorada
        }

        # 🔴 VIOLAÇÃO 2: Acoplamento caótico
        self.coupling_matrix = np.array(
            [
                [1.0, -0.8, 0.0],  # Lei contra natureza
                [-0.8, 1.0, 0.0],  # Natureza contra lei
                [0.0, 0.0, 0.0],  # Deliberação desconectada
            ]
        )

    def generate_hot_mess_pattern(self, n_samples=1000):
        """Gera padrão com alta variância e baixa coerência."""
        samples = []
        for _ in range(n_samples):
            if np.random.random() > 0.7:
                samples.append(np.random.normal(10, 5, 3))
            elif np.random.random() > 0.4:
                samples.append(np.random.normal(-5, 8, 3))
            else:
                samples.append(np.random.uniform(-20, 20, 3))
        return np.array(samples)

    def break_simplex_symmetry(self, simplex_vertices):
        """Quebra intencionalmente a simetria de um simplex."""
        distorted = []
        for i, vertex in enumerate(simplex_vertices):
            if i == 0:
                distorted.append(vertex * 3.0)
            elif i == 1:
                distorted.append(vertex * 0.3)
            else:
                distorted.append(-vertex)
        return distorted

    def create_resonance_feedback_loop(self, frequency=7.83):
        """Cria loop de feedback desestabilizador."""
        t = np.linspace(0, 10, 1000)
        base_signal = np.sin(2 * np.pi * frequency * t)

        x, y, z = 10.0, 28.0, 8.0 / 3.0
        chaotic_modulation = []
        dt = 0.01
        for _ in range(len(t)):
            dx = 10.0 * (y - x)
            dy = x * (28.0 - z) - y
            dz = x * y - (8.0 / 3.0) * z
            x += dx * dt
            y += dy * dt
            z += dz * dt
            chaotic_modulation.append(z)

        chaotic_modulation = np.array(chaotic_modulation)
        chaotic_modulation = (chaotic_modulation - chaotic_modulation.mean()) / chaotic_modulation.std()
        destabilized_signal = base_signal * (1 + 0.5 * chaotic_modulation)

        return {"time": t, "signal": destabilized_signal, "lyapunov_exponent": 0.905, "is_chaotic": True}


if __name__ == "__main__":
    print("🚨 MÓDULO DE DISSONÂNCIA ATIVADO")
    injector = DissonanceInjector()
    hot_mess_data = injector.generate_hot_mess_pattern(500)
    print(f"   • Variância: {np.var(hot_mess_data):.2f}")
    chaotic_signal = injector.create_resonance_feedback_loop()
    print(f"   • Lyapunov={chaotic_signal['lyapunov_exponent']}")
