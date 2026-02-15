"""
Unit tests for the Arkhe module.
Verifies UCD, RFID, Arkhen11, and Swimmer logic.
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
from talos.arkhe.arkhen_11 import Arkhen11
from talos.arkhe.rfid import RFIDHypergraph, RFIDTag
from talos.arkhe.swimmer import FlagellarSwimmer
from talos.arkhe.ucd import UCD, verify_conservation


def test_ucd_conservation() -> None:
    """Tests if C + F = 1 holds in UCD."""
    data = np.random.rand(10, 5)
    ucd = UCD(data)
    result = ucd.analyze()
    assert verify_conservation(result["C"], result["F"])


def test_rfid_geodesic() -> None:
    """Tests if RFID tag correctly records its path."""
    tag = RFIDTag("T001", "asset")
    tag.read("R1", "LocA", timestamp=datetime(2024, 1, 1, 10, 0))
    tag.read("R2", "LocB", timestamp=datetime(2024, 1, 1, 11, 0))
    assert tag.get_path_history() == ["LocA", "LocB"]
    assert tag.verify_conservation()


def test_arkhen11_metrics() -> None:
    """Tests core metrics of the Arkhen(11) model."""
    arkhen = Arkhen11()
    coherence = arkhen.compute_coherence()
    dim = arkhen.compute_effective_dimension()
    assert 0 < coherence < 1
    assert dim > 0
    assert arkhen.verify_conservation()


def test_swimmer_propulsion() -> None:
    """Tests if the flagellar swimmer generates displacement."""
    swimmer = FlagellarSwimmer(length=10.0, dt=0.1)
    x_hist, _, _ = swimmer.run(t_max=1.0)
    # The swimmer should move (displacement > 0)
    # For a wave traveling right, it usually moves left (negative x)
    assert abs(x_hist[-1] - x_hist[0]) > 0


def test_rfid_hypergraph() -> None:
    """Tests the RFIDHypergraph registration and anomaly detection."""
    h_graph = RFIDHypergraph()
    tag = RFIDTag("T1", "item")
    h_graph.add_tag(tag)
    h_graph.register_reading("T1", "R1", "Warehouse")
    assert "T1" in h_graph.tags
    assert "Warehouse" in h_graph.locations
    assert not h_graph.identify_anomalies()
