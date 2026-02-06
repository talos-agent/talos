from __future__ import annotations

import pytest
from talos.geometric_core.vitality import UrbanPulse, NoiseSensor
from talos.geometric_core.urban_optimizer import UrbanOptimizer, RouteNode


def test_urban_optimizer_route():
    pulse = UrbanPulse(city_name="Test City")
    pulse.sensors.append(NoiseSensor(name="N1", location="L1"))

    optimizer = UrbanOptimizer(pulse=pulse)
    nodes = [
        RouteNode(id=1, lat=0.0, lon=0.0),
        RouteNode(id=2, lat=1.0, lon=1.0),
    ]

    route = optimizer.calculate_ethical_route(nodes)
    assert len(route) == 2
    assert route[0].vitality >= route[1].vitality


def test_sophia_glow_activation():
    pulse = UrbanPulse(city_name="Test City")
    optimizer = UrbanOptimizer(pulse=pulse)

    msg = optimizer.activate_sophia_glow()
    assert optimizer.sophia_glow_active is True
    assert "Sophia Glow Activated" in msg
