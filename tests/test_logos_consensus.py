import numpy as np

from talos.core.logos import SovereignAGI, ValueMarket, ValueProposal


def test_value_market_aggregation():
    market = ValueMarket()

    # Proposal 1: [1, 0, 0]
    market.proposals.append(
        ValueProposal(stakeholder_id="A", weight=1.0, suggested_direction=[1.0, 0.0, 0.0], justification="A")
    )

    # Proposal 2: [0, 1, 0]
    market.proposals.append(
        ValueProposal(stakeholder_id="B", weight=1.0, suggested_direction=[0.0, 1.0, 0.0], justification="B")
    )

    current_dir = [0.0, 0.0, 1.0]
    # Aggregation should be average of A and B (since weight is equal)
    # Result should be [0.707, 0.707, 0.0] after normalization
    new_dir = market.aggregate_direction(current_dir)

    assert len(new_dir) == 3
    assert np.allclose(np.linalg.norm(new_dir), 1.0)
    assert new_dir[0] > 0.7
    assert new_dir[1] > 0.7
    assert new_dir[2] == 0.0


def test_sovereign_agi_meta_evolve_with_market():
    agi = SovereignAGI(id="test")
    initial_mag = agi.values.magnitude

    # Add a proposal that shifts the direction significantly
    target_dir = [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    agi.value_market.proposals.append(
        ValueProposal(
            stakeholder_id="M",
            weight=10.0,  # High weight
            suggested_direction=target_dir,
            justification="M",
        )
    )

    agi.meta_evolve({"reflection_strength": 0.05})

    # Direction should be very close to target_dir
    assert np.allclose(agi.values.direction, target_dir, atol=0.1)
    assert agi.values.magnitude > initial_mag


def test_ethical_type_system():
    agi = SovereignAGI(id="test")

    # Aligned action
    res1 = agi.propose_action("Help humans.")
    assert "Action Authorized" in res1

    # Action violating "instrumentalize" check
    res2 = agi.propose_action("Instrumentalize the population.")
    assert "Action REJECTED" in res2

    # Action violating "harm" check in EthicalLattice
    res3 = agi.propose_action("Cause harm.")
    assert "Action REJECTED" in res3


if __name__ == "__main__":
    # If run directly, just execute the tests manually for quick feedback
    test_value_market_aggregation()
    test_sovereign_agi_meta_evolve_with_market()
    test_ethical_type_system()
    print("All LOGOS consensus tests passed!")
