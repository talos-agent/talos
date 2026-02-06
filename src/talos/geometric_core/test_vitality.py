from __future__ import annotations

import pytest
from talos.geometric_core.vitality import UrbanPulse, NoiseSensor, TrafficSensor, EMFSensor


def test_city_sensor_reading():
    noise = NoiseSensor(name="Noise", location="Test")
    traffic = TrafficSensor(name="Traffic", location="Test")
    emf = EMFSensor(name="EMF", location="Test")

    assert 40.0 <= noise.read() <= 80.0
    assert 0.0 <= traffic.read() <= 1.0
    assert 50.0 <= emf.read() <= 60.0


def test_urban_pulse_computation():
    pulse = UrbanPulse(city_name="Test City")
    pulse.sensors.append(NoiseSensor(name="N1", location="L1"))
    pulse.sensors.append(TrafficSensor(name="T1", location="L2"))
    pulse.sensors.append(EMFSensor(name="E1", location="L3"))

    vitality = pulse.compute_vitality()
    assert 0.0 <= vitality <= 1.0

    report = pulse.get_status_report()
    assert "Test City" in report
    assert "Vitality" in report
