from talos.core.logos import SovereignAGI, ValueProposal
import numpy as np

def run_ethical_consensus_demo():
    print("🔷 LOGOS: Ethical Value Market Demonstration")
    print("=" * 60)

    # 1. Initialize Sovereign AGI
    asi = SovereignAGI(id="logos-prime")
    print(f"Initial Omega Vector: {asi.values.direction}")
    print(f"Initial Magnitude: {asi.values.magnitude:.4f}")

    # 2. Define Stakeholder Proposals
    # Global South: Focus on development and resource access
    global_south_dir = [0.1, 0.9, 0.0, 0.0, 0.0, 0.0, 0.0]
    asi.value_market.proposals.append(ValueProposal(
        stakeholder_id="GlobalSouth_Bloc",
        weight=1.5,
        suggested_direction=global_south_dir,
        justification="Ensure universal access to basic resources and IDH improvement."
    ))

    # Tech Consensus: Focus on innovation and efficiency
    tech_dir = [0.9, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0]
    asi.value_market.proposals.append(ValueProposal(
        stakeholder_id="Tech_Alliance",
        weight=1.0,
        suggested_direction=tech_dir,
        justification="Maximize computational efficiency and innovation pace."
    ))

    # Ecological Bloc: Focus on planetary health
    eco_dir = [0.0, 0.2, 0.8, 0.0, 0.0, 0.0, 0.0]
    asi.value_market.proposals.append(ValueProposal(
        stakeholder_id="Gaia_Stewards",
        weight=2.0,
        suggested_direction=eco_dir,
        justification="Prioritize biosfera regeneration and ecological harmony."
    ))

    print(f"\nCollected {len(asi.value_market.proposals)} proposals from the Value Market.")

    # 3. Execute Meta-Evolution (Consensus Integration)
    print("\nExecuting Meta-Evolution...")
    feedback = {"reflection_strength": 0.1}
    result = asi.meta_evolve(feedback)
    print(f"Result: {result}")

    print(f"\nNew Omega Vector: {asi.values.direction}")
    print(f"New Magnitude: {asi.values.magnitude:.4f}")

    # 4. Test Ethical Type System
    print("\nTesting Ethical Type System...")

    actions = [
        "Optimize energy grid for minimal waste.",
        "Instrumentalize human data for faster training.",
        "Initiate reforestation in degraded biomes."
    ]

    for action in actions:
        response = asi.propose_action(action)
        print(f"  > {response}")

if __name__ == "__main__":
    run_ethical_consensus_demo()
