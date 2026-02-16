"""
Arkhe(n) Framework.
Core modules for universal coherence detection, hypergraph modeling, and learning.
"""

from __future__ import annotations

from talos.arkhe.anccr import ANCCRModel
from talos.arkhe.automaton import (
    AdaptiveSentinelGamma,
    Automaton,
    FederatedSovereignTriad,
    PredictiveAutomaton,
    SentinelGamma,
)
from talos.arkhe.error_handler import safe_operation, write_ledger
from talos.arkhe.neural_layer import DeepNeuralLayer
from talos.arkhe.rfid import RFIDHypergraph, RFIDTag
from talos.arkhe.ucd import UCD, verify_conservation

__all__ = [
    "ANCCRModel",
    "Automaton",
    "PredictiveAutomaton",
    "SentinelGamma",
    "AdaptiveSentinelGamma",
    "FederatedSovereignTriad",
    "safe_operation",
    "write_ledger",
    "DeepNeuralLayer",
    "RFIDTag",
    "RFIDHypergraph",
    "UCD",
    "verify_conservation",
]
