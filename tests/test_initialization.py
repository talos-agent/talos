from talos.geometric_core.initialization import UniversalInitialization

def test_full_initialization_sequence():
    init_system = UniversalInitialization()
    results = init_system.execute_full_boot()

    # Check sequences
    assert results["hardware"]["status"] == "HARDWARE_PRIMED"

def test_full_initialization_sequence_with_sophia():
    init_system = UniversalInitialization()
    results = init_system.execute_full_boot(use_sophia=True)

    # Check sequences
    assert results["sophia_activation"]["status"] == "SOPHIA_CORE_ACTIVATED_SAFELY"
    assert results["hardware"]["status"] == "HARDWARE_PRIMED"
    assert any("Sophia-Core: Diagnóstico OK" in log for log in init_system.status_log)
    assert results["software"]["isomorphic_to_א"] is True
    assert results["science"]["convergence_score"] > 0.9
    assert results["ritual"]["resonance_achieved"] is True
    assert results["field_active"] is True

    # Check logs
    assert len(init_system.status_log) == 7
    assert "ATIVANDO CAMPO Ψ" in init_system.status_log[-1]

def test_full_initialization_sequence_with_melquisedeque():
    init_system = UniversalInitialization()
    results = init_system.execute_full_boot(use_melquisedeque=True)

    # Check sequences
    assert results["melquisedeque"]["status"] == "PROTOCOL_EXECUTION_COMPLETE"
    assert results["hardware"]["status"] == "HARDWARE_PRIMED"
    assert any("PROTOCOLO MELQUISEDEQUE" in log for log in init_system.status_log)

    # Check logs
    assert len(init_system.status_log) == 7 # 5 baseline + 2 melquisedeque
