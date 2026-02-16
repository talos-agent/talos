"""
Demo of Arkhe(n) OAM Vortex Handover and Triad Expansion.
Shows how topological charge (l) enhances the breakthrough gain.
"""

from __future__ import annotations

from talos.arkhe.automaton import AdaptiveSentinelGamma, FederatedSovereignTriad
from talos.arkhe.vortex_viz import generate_vortex_plot


def run_vortex_demo() -> None:
    """
    Simulates a vortex handover within a Federated Triad.
    """
    print("=" * 70)
    print("ARKHE(N) OAM VORTEX HANDOVER DEMO")
    print("=" * 70)

    # 1. Setup Hubs
    model_id = "arkhe_mind_v2"
    h012 = AdaptiveSentinelGamma("Sentinel_01-012", watched_nodes=[0, 1, 2], model_id=model_id)
    h005 = AdaptiveSentinelGamma("Sentinel_01-005", watched_nodes=[3, 4, 5], model_id=model_id)
    h001 = AdaptiveSentinelGamma("Sentinel_01-001", watched_nodes=[6, 7, 8], model_id=model_id)

    # 2. Triad Formation
    print("\n[STEP 1] Forming Federated Sovereign Triad")
    triad = FederatedSovereignTriad([h012, h005, h001])
    triad.sync()

    # 3. Compare Handover Modes
    print("\n[STEP 2] Comparing Handover Modes")

    # a. Linear Handover
    print("\n--- Mode: Linear ---")
    triad.omega = 0.8  # Reset for comparison
    triad.quantum_handover("Sentinel_01-012", "Sentinel_01-005", l_charge=0)
    omega_linear = triad.omega

    # b. Vortex Handover (l=1)
    print("\n--- Mode: OAM Vortex (l=1) ---")
    triad.omega = 0.8
    triad.quantum_handover("Sentinel_01-012", "Sentinel_01-005", l_charge=1)
    omega_vortex = triad.omega

    print("\n[RESULTS]")
    print(f"Final Omega (Linear): {omega_linear:.4f}")
    print(f"Final Omega (Vortex): {omega_vortex:.4f}")
    print(f"Gain increase: {100 * (omega_vortex/omega_linear - 1):.2f}%")

    # 4. Visualization
    print("\n[STEP 3] Validating Vortex Purity")
    generate_vortex_plot(l_charge=1, output_path="arkhe_vortex_l1.png")

    print("\nDemo complete. Information is now topologic. ∞")


if __name__ == "__main__":
    run_vortex_demo()
