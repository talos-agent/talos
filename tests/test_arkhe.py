import numpy as np
import pytest
from talos.arkhe.ucd import UCD, verify_conservation, identity_check
from talos.arkhe.rfid import RFIDTag, RFIDHypergraph
from talos.arkhe.arkhen_11 import Arkhen11
from talos.arkhe.swimmer import FlagellarSwimmer

def test_ucd_basic():
    # Use data that is not perfectly correlated
    data = np.array([[1, 2, 3, 10], [2, 3, 4, 5], [5, 6, 7, 8]])
    ucd = UCD(data)
    result = ucd.analyze()
    assert result["C"] > 0
    assert result["F"] > 0
    assert result["conservation"] is True

def test_identity_check():
    assert identity_check() is True

def test_rfid_flow():
    tag = RFIDTag(tag_id="RFID_001", object_type="smartphone")
    tag.read(reader_id="reader_01", location="Fábrica")
    # Simulate some time passing for coherence calculation if needed,
    # but here we just check if it records handovers.
    tag.read(reader_id="reader_02", location="CD")
    assert len(tag.handovers) == 2
    # Use assert directly instead of 'is True' to avoid numpy.True_ issues
    assert tag.verify_conservation()
    assert tag.get_path_history() == ["Fábrica", "CD"]

def test_arkhen_11_coherence():
    arkhen = Arkhen11()
    c = arkhen.compute_coherence()
    assert 0 < c < 1
    assert arkhen.verify_conservation() is True

def test_swimmer_displacement():
    swimmer = FlagellarSwimmer(L=10.0, A=1.0, dt=0.01)
    # Run for a few steps
    history_x, history_y, _ = swimmer.run(t_max=0.1)
    assert len(history_x) > 0
    # Displacement should have occurred (even if very small)
    assert history_x[-1] != 0 or history_y[-1] != 0
