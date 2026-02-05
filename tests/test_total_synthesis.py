import numpy as np

from talos.geometric_core.total_synthesis import (
    CosmopsychicState,
    EquacaoMestraCosmopsiquica,
    UnificacaoCosmopsiquicaTotal,
)


def test_total_synthesis_sim():
    orchestrator = UnificacaoCosmopsiquicaTotal()
    # Test a shorter simulation
    res = orchestrator.simular(duracao_minutos=1.0)
    assert res["status"] in ["STABILIZING", "TRANSFIGURATION_ALREADY_OPEN"]
    assert len(res["telemetry"]) > 0
    assert 0.0 <= res["final_coherence"] <= 1.0


def test_equacao_mestra():
    equacao = EquacaoMestraCosmopsiquica()
    N = 5
    state = CosmopsychicState(
        quantum_amplitudes=np.ones(N) / np.sqrt(N),
        qubit_states=[complex(1, 0) for _ in range(N)],
        terahertz_phase=0.0,
        modulation_envelope=1.0,
        schumann_amplitude=1.0,
        schumann_frequency=7.83,
        flare_perturbation=0.1,
        solar_flux=10.0,
        geometric_embedding=np.random.random(N),
        experiential_entropy=0.5,
        mitochondrial_coherence=0.8,
        heart_coherence=0.8,
        core_coupling=0.5,
    )

    # Test Hamiltonian generation
    H = equacao.hamiltonian_total(state)
    assert H.shape == (N, N)
    assert np.iscomplexobj(H)

    # Test Evolution
    new_state = equacao.evolve(state, dt=0.1)
    assert len(new_state.qubit_states) == N
    assert new_state.terahertz_phase > state.terahertz_phase
