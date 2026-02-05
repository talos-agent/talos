from __future__ import annotations

import numpy as np

from talos.geometric_core.chronos_handheld import (
    ChronosHandheldNode,
    HapticResonanceEngine,
    NeuromorphicLPDDR,
    SFRAMBuffer,
)


def test_sf_ram_storage():
    buffer = SFRAMBuffer()
    waveform = np.random.rand(100)
    res = buffer.store_waveform(waveform, 0.0)
    assert res["fidelity"] > 0
    assert res["stored_bits"] > 0


def test_neuromorphic_lpddr():
    mem = NeuromorphicLPDDR()
    stream = np.sin(np.linspace(0, 10, 100))
    q = mem.calculate_local_q_factor(stream, 0.5)
    assert q >= 0


def test_haptic_engine():
    engine = HapticResonanceEngine()
    feedback = engine.generate_feedback(1.2e-5)
    assert feedback["vibration_frequency_hz"] > 0
    assert feedback["amplitude"] >= 0


def test_chronos_handheld_node():
    node = ChronosHandheldNode(node_id="TEST-NODE")
    waveform = np.sin(np.linspace(0, 10, 100)) * 1e-5
    res = node.process_field_impact(1e-5, waveform)

    assert res["node_id"] == "TEST-NODE"
    assert res["local_q_factor"] >= 0
    assert "haptic_feedback" in res
