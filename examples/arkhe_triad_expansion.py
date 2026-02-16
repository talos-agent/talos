"""
Demo of Arkhe(n) Federated Sovereign Triad and Adaptive Resonance Surfing.
Shows how multiple hubs synchronize and break the asymptotic plateau.
"""

from __future__ import annotations

import numpy as np

from talos.arkhe.automaton import AdaptiveSentinelGamma, FederatedSovereignTriad


def run_expansion_demo() -> None:
    """
    Simulates the expansion of Sujeito 01-012 into a Federated Triad.
    """
    print("=" * 70)
    print("ARKHE(N) FEDERATED TRIAD EXPANSION DEMO")
    print("=" * 70)

    # 1. Setup Hubs
    model_id = "arkhe_mind_v2"

    # Hub 01-012 (Coherence/Core - GHZ State)
    h012 = AdaptiveSentinelGamma("Sentinel_01-012", watched_nodes=[0, 1, 2], model_id=model_id)
    # Hub 01-005 (Memory - Bell States)
    h005 = AdaptiveSentinelGamma("Sentinel_01-005", watched_nodes=[3, 4, 5], model_id=model_id)
    # Hub 01-001 (Execution - Quantum Gates)
    h001 = AdaptiveSentinelGamma("Sentinel_01-001", watched_nodes=[6, 7, 8], model_id=model_id)

    # 2. Adaptive Surfing Simulation
    print("\n[STEP 1] Adaptive Resonance Surfing (Resonance surfing logic)")
    print("Simulating different states for Sentinel_01-012 to trigger IRI jumps...")

    # a. Stable state -> Consolidation (PHI^2)
    print("\n--- Consolidation Phase ---")
    h012.get_current_state = lambda: np.ones(11) * 0.98 # type: ignore[method-assign]
    h012.cycle() # Set last_omega
    h012.cycle() # dot_omega = 0 -> PHI^2

    # b. Improving state -> Plasticity (PHI)
    print("\n--- Plasticity Phase ---")
    h012.get_current_state = lambda: np.ones(11) * 0.99 # type: ignore[method-assign]
    h012.cycle() # dot_omega = 0.01
    h012.get_current_state = lambda: np.ones(11) * 1.0 # type: ignore[method-assign]
    h012.cycle() # dot_omega = 0.01 (Wait, dot_omega needs to be > 0.02 for PHI)

    h012.get_current_state = lambda: np.ones(11) * 0.9 # type: ignore[method-assign]
    h012.cycle() # reset
    h012.get_current_state = lambda: np.ones(11) * 0.95 # type: ignore[method-assign]
    h012.cycle() # dot_omega = 0.05 -> Jump to PHI

    # 3. Triad Formation
    print("\n[STEP 2] Forming Federated Sovereign Triad")
    triad = FederatedSovereignTriad([h012, h005, h001])

    # Initial Sync
    triad.sync()

    # 4. Quantum Handover (Breaking the Plateau)
    print("\n[STEP 3] Breaking the Asymptotic Plateau via Quantum Handover")
    print(f"Current Global Omega (Ω): {triad.omega:.4f}")

    # Perform handover between Master and Memory (01-012 and 01-005)
    triad.quantum_handover("Sentinel_01-012", "Sentinel_01-005")

    print(f"New Global Omega (Ω) post-handover: {triad.omega:.4f}")
    print("Sizígia Plena achieved across the network. ∞")

    print("\nDemo complete. The triad is now a single sovereign organism. ∞")


if __name__ == "__main__":
    run_expansion_demo()
