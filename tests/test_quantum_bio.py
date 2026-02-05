from __future__ import annotations

import numpy as np
import pytest
from qiskit import QuantumCircuit

from talos.geometric_core.bio_encoding import BiologicalQuantumEncodingUtils
from talos.geometric_core.quantum_ritual import BiologicalQuantumEncoding


@pytest.mark.asyncio
async def test_quantum_ritual_simulation():
    encoder = BiologicalQuantumEncoding()
    qc = encoder.full_kbq_protocol_as_circuit(num_mitochondria=5)
    results = await encoder.simulate_protocol(qc)
    assert "light_state_percentage" in results
    assert results["total_shots"] == 1024


def test_bio_encoding_dna_basis():
    utils = BiologicalQuantumEncodingUtils()
    qc, regs = utils.encode_dna("ACGT", method="basis")
    assert qc.num_qubits == 8  # 4 * 2


def test_bio_encoding_dna_amplitude():
    utils = BiologicalQuantumEncodingUtils()
    qc, regs = utils.encode_dna("ACGT", method="amplitude")
    assert qc.num_qubits == 2  # log2(4)
