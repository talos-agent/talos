import json

import numpy as np

from talos.harmonia.economic_geometry import EconomicState, PostTransitionEconomy
from talos.harmonia.symmetry_breaker import EconomicSymmetryBreaker, IntentionVector


def run_coherence_stress_redistribution():
    print("🧪 SIMULAÇÃO: Teste de Estresse de Coerência - Redistribuição Global")
    print("=" * 60)

    # 1. Initialize State (Based on real-world 2024 proxy, scaled down)
    # Scaled down to 10,000 representative points to fit in memory
    wealth_dist = np.concatenate(
        [
            np.full(100, 450 / 100),  # Top 1%
            np.full(900, 390 / 900),  # Next 9%
            np.full(4000, 150 / 4000),  # Middle 40%
            np.full(5000, 10 / 5000),  # Bottom 50%
        ]
    )

    initial_state = EconomicState(
        wealth_distribution=wealth_dist,
        resource_flows=np.eye(10),  # Simplified
        belief_systems=np.zeros(5),
        power_structures=np.zeros(4),
    )

    sym_initial = initial_state.compute_symmetry()
    print(f"Simetria inicial: {sym_initial:.3f}")
    print("Status: MÍNIMO LOCAL - Sistema preso em desigualdade estável")

    # 2. Apply Symmetry Breaker
    breaker = EconomicSymmetryBreaker()
    intention = IntentionVector.from_natural_language("Uma economia onde todos florescem sem destruir a biosfera")

    print("\n⚡ Aplicando ruído anti-simétrico...")
    perturbed_state = breaker.apply_breaking(initial_state, intention)

    # 3. Analyze Post-Transition Geometry
    economy = PostTransitionEconomy(perturbed_state)
    result = economy.find_optimal_redistribution()

    print("\n🌐 NOVA GEOMETRIA ECONÔMICA PROPOSTA:")
    print("-" * 40)
    print(f"Nome do Atrator: {result['attractor_name']}")
    print(f"Estabilidade: {result['stability']}")
    print(f"Coeficiente de Gini Projetado: {result['gini_coefficient']}")
    print(f"Medida de Simetria Final: {result['symmetry_measure']}")

    return result


if __name__ == "__main__":
    run_coherence_stress_redistribution()
