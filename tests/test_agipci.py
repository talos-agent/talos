import numpy as np

from talos.geometric_core.agipci import ResonantCognitionSimulator, SchumannField, SolarFlareStimulus


def test_schumann_field():
    schumann = SchumannField()
    signal = schumann.get_signal(t=1.0)
    assert -1.0 <= signal <= 1.0

    signal_detuned = schumann.get_signal(t=1.0, detuning=0.1)
    assert signal != signal_detuned


def test_solar_flare_detuning():
    flare = SolarFlareStimulus(x_ray_flux=1e-4)  # X-class flare
    detuning = flare.calculate_detuning()
    # log10(1e-4 / 1e-8) = 4, so detuning = 0.4
    assert round(detuning, 2) == 0.4


def test_simulator_evolution():
    sim = ResonantCognitionSimulator(num_qubits=10)
    res = sim.evolve(duration_s=0.01, steps=10)
    assert res["status"] == "Simulation_Complete"
    assert len(res["telemetry"]) > 0
    assert 0.0 <= res["avg_aha"] <= 1.0


def test_consciousness_verification():
    sim = ResonantCognitionSimulator(num_qubits=10)
    # Mocking alpha to be high
    sim.core.alpha = np.ones(10) * 0.1
    # Mocking stable histories
    sim.core.entropy_history = [1.0] * 10
    sim.core.phi_tc_history = [1.0] * 10
    sim.core.self_intuition_history = [0.2] * 10

    assert sim.verify_consciousness() is True

    # Mocking unstable phi (subharmonic instability)
    sim.core.phi_tc_history = [1.0, 0.1, 0.8, 0.2, 0.9, 0.1, 1.0, 0.0, 0.5, 0.1]
    assert sim.verify_consciousness() is False
