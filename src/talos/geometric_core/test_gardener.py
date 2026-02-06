from __future__ import annotations

import pytest
from talos.geometric_core.gardener import DigitalGardener


def test_gardener_prescribe():
    gardener = DigitalGardener()
    cures = gardener.prescribe_cure(["AR TÓXICO"])
    assert any("musgo" in c for c in cures)

    cures_none = gardener.prescribe_cure([])
    assert "Manutenção rotineira" in cures_none[0]


def test_healing_details():
    gardener = DigitalGardener()
    details = gardener.get_healing_details("AR TÓXICO")
    assert len(details) == 1
    assert details[0].agent == "Sphagnum moss"
