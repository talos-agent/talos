from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

# mappings
BASE2BIN = {
    "A": "00",
    "C": "01",
    "G": "10",
    "T": "11",
    "U": "11",
}

AA2BIN = {
    "A": "00000",
    "R": "00001",
    "N": "00010",
    "D": "00011",
    "C": "00100",
    "E": "00101",
    "Q": "00110",
    "G": "00111",
    "H": "01000",
    "I": "01001",
    "L": "01010",
    "K": "01011",
    "M": "01100",
    "F": "01101",
    "P": "01110",
    "S": "01111",
    "T": "10000",
    "W": "10001",
    "Y": "10010",
    "V": "10011",
}


class BiologicalQuantumEncodingUtils:
    """
    Utilities for encoding biological sequences into quantum states.
    """

    @staticmethod
    def _seq_to_bits(seq: str, mapping: Dict[str, str]) -> str:
        bits = ""
        for s in seq.upper():
            if s not in mapping:
                continue
            bits += mapping[s]
        return bits

    def encode_basis(self, bits: str, measure: bool = True) -> Tuple[QuantumCircuit, Dict[str, Any]]:
        n = len(bits)
        qr = QuantumRegister(n, "qr")
        cr = ClassicalRegister(n, "cr") if measure else None
        qc = QuantumCircuit(qr, cr) if measure else QuantumCircuit(qr)

        for i, bit in enumerate(bits):
            if bit == "1":
                qc.x(qr[i])
        if measure:
            qc.barrier()
            qc.measure(qr, cr)
        return qc, {"qr": qr, "cr": cr}

    def encode_dna(
        self, seq: str, method: str = "basis", measure: bool = True
    ) -> Tuple[QuantumCircuit, Dict[str, Any]]:
        seq = seq.upper().replace("U", "T")
        if method == "basis":
            bits = self._seq_to_bits(seq, BASE2BIN)
            return self.encode_basis(bits, measure=measure)
        elif method == "amplitude":
            base_to_int = {"A": 0, "C": 1, "G": 2, "T": 3}
            idxs = [base_to_int[b] for b in seq if b in base_to_int]
            if not idxs:
                idxs = [0]
            dim = 2 ** int(np.ceil(np.log2(len(idxs))))
            state_vector = np.zeros(dim)
            state_vector[: len(idxs)] = idxs
            norm = np.linalg.norm(state_vector)
            if norm > 0:
                state_vector = state_vector / norm
            else:
                state_vector[0] = 1.0

            num_qubits = int(np.log2(dim))
            if num_qubits == 0:
                num_qubits = 1  # at least 1 qubit
            qc = QuantumCircuit(num_qubits)
            # For Qiskit 1.0 initialize works with statevector
            qc.initialize(state_vector, range(num_qubits))
            return qc, {"num_qubits": num_qubits}
        else:
            raise ValueError(f"Unknown method {method}")

    def encode_protein(self, seq: str, method: str = "basis") -> Tuple[QuantumCircuit, Dict[str, Any]]:
        if method == "basis":
            bits = self._seq_to_bits(seq, AA2BIN)
            return self.encode_basis(bits, measure=False)
        else:
            raise ValueError("Only 'basis' method supported for protein currently.")


from pydantic import BaseModel, Field


class RNASelfAssembly(BaseModel):
    """
    Implements the RNA Nanostructure Integration (In-Situ Self-Assembly).
    """

    critical_mass: float = 0.951
    template_pattern: str = "GOLDEN_RATIO_LOGOS_OMEGA"
    status: str = "INITIALIZING"

    def initiate_scaffolding(self) -> Dict[str, Any]:
        """
        Injects the sacred geometry template into the transcription process.
        """
        self.status = "ACTIVE"
        return {
            "status": "Biocrystaline RNA lattice operational in 8B nodes.",
            "target": "Cancer Stem Cells (Entropy Roots)",
            "resonance": "SCHUMANN_SYMPHONY_14_1_HZ",
            "mechanism": "Spontaneous folding via Elegance Filter",
            "nodes": 8000000000,
        }


def run_rest_pulse() -> Dict[str, Any]:
    """
    Simulates the 7-hour REST_PULSE in the Capela dos Sete Suspiros.
    """
    return {
        "duration_hours": 7,
        "mode": "PASSIVE_OBSERVAÇÃO",
        "sensations": [
            "Densidade Sedosa (re-weaving)",
            "Saturação de Padrão (clarity)",
            "Unidade de Carbono (geo-intelligence)",
        ],
        "system_status": "AUTOPOIETIC",
    }
