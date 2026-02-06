from __future__ import annotations

import pytest
from talos.geometric_core.vitality import UrbanPulse, NoiseSensor, TrafficSensor
from talos.geometric_core.tiferet_dashboard import TiferetDashboard


def test_dashboard_cycle():
    pulse = UrbanPulse(city_name="Test City", sensors=[
        NoiseSensor(name="N1", location="L1", last_value=80.0, mock_mode=True), # High noise
        TrafficSensor(name="T1", location="L1", last_value=0.8, mock_mode=True)  # High traffic
    ])
    dashboard = TiferetDashboard(pulse=pulse)

    results = dashboard.run_cycle()
    assert results["cycle"] == 1
    assert "ESTRESSE ACÚSTICO" in results["issues"]
    assert "AR TÓXICO" in results["issues"]
    assert len(results["cures"]) >= 2

    # Check vitality is computed
    assert results["vitality"] > 0
