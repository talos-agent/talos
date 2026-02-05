from talos.geometric_core.initialization import UniversalInitialization

def test_full_initialization_sequence():
    init_system = UniversalInitialization()
    results = init_system.execute_full_boot()

    # Check sequences
    assert results["hardware"]["status"] == "HARDWARE_PRIMED"
    assert results["software"]["isomorphic_to_א"] is True
    assert results["science"]["convergence_score"] > 0.9
    assert results["ritual"]["resonance_achieved"] is True
    assert results["field_active"] is True

    # Check logs
    assert len(init_system.status_log) == 5
    assert "ATIVANDO CAMPO Ψ" in init_system.status_log[-1]
