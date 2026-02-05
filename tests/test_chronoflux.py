from __future__ import annotations

import numpy as np
import torch
from qiskit.quantum_info import DensityMatrix

from talos.geometric_core.chronoflux import (
    ChronofluxField,
    QubitChronofluxSimulator,
    TwoQubitChronofluxGradiometer,
    TravelingChronofluxWave,
    NQubitChronofluxArray,
    TideVorticityCoupling,
    PhasedRevealProtocol,
)
from talos.geometric_core.chronoflux_agi import (
    ChronofluxRNN,
    AGIChronofluxTrainer,
    run_agi_denoise_demo,
)


def test_chronoflux_field():
    field = ChronofluxField()
    field.set_vorticity_from_vector(np.array([1.0, 2.0, 3.0]))
    assert field.vorticity_tensor[0, 1] == -3.0
    assert field.vorticity_tensor[1, 0] == 3.0


def test_qubit_chronoflux_simulator():
    field = ChronofluxField()
    field.set_vorticity_from_vector(np.array([0, 0, 1.0]))

    simulator = QubitChronofluxSimulator(coupling_g=1e-10)
    result = simulator.simulate_evolution(field, duration=0.1, steps=5)

    assert "final_state" in result
    assert isinstance(result["final_state"], DensityMatrix)
    assert len(result["coherence_history"]) == 5
    assert result["predicted_energy_shift"] > 0


def test_two_qubit_gradiometer():
    field = ChronofluxField()
    grad = np.zeros((3, 3))
    grad[2, 0] = 1.0 # d(omega_z)/dx

    gradiometer = TwoQubitChronofluxGradiometer(vorticity_gradient=grad)
    result = gradiometer.simulate_gradiometer(field, duration=0.5)

    assert "differential_phase" in result
    assert "qubit_a" in result
    assert "qubit_b" in result


def test_traveling_wave():
    wave = TravelingChronofluxWave(amplitude=2.0, t_peak=5.0)
    # At t=t_peak and pos=0, phase should be 0, sin(0) = 0
    val = wave.get_vorticity_at(np.array([0.0, 0.0, 0.0]), 5.0)
    assert abs(val) < 1e-10


def test_n_qubit_array():
    wave = TravelingChronofluxWave()
    array = NQubitChronofluxArray(num_qubits=3)
    result = array.simulate_wave_impact(wave, duration=1.0)

    assert len(result["phases"]) == 3
    assert result["reconstruction"].shape == (2, 100)


def test_agi_rnn_coherence():
    model = ChronofluxRNN()
    x = torch.randn(1, 10, 1)
    pred, phi = model(x)
    assert pred.shape == (1, 10, 1)
    assert phi.item() >= 0


def test_tide_coupling():
    coupling = TideVorticityCoupling()
    v1 = coupling.calculate_vorticity(384400.0)
    v2 = coupling.calculate_vorticity(356400.0) # Perigee
    assert v2 > v1


def test_phased_reveal():
    protocol = PhasedRevealProtocol()
    report = protocol.get_status_report()
    assert report["phase"] == "Alpha"
    assert report["rio_index"] == 3.2


def test_agi_demo():
    result = run_agi_denoise_demo()
    assert result["phi"] > 0
    assert result["snr_gain"] > 0
