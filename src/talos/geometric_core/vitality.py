from __future__ import annotations

import time
from abc import ABC, abstractmethod
import numpy as np
from pydantic import BaseModel, ConfigDict, Field


class CitySensor(ABC, BaseModel):
    """
    Abstract base class for city sensors.
    """
    name: str
    location: str
    last_value: float = 0.0
    timestamp: float = Field(default_factory=time.time)
    mock_mode: bool = False

    @abstractmethod
    def read(self) -> float:
        """Reads the current value from the sensor."""
        pass


class NoiseSensor(CitySensor):
    """
    Monitors urban noise levels in decibels (dB).
    """
    def read(self) -> float:
        if self.mock_mode:
            return self.last_value
        # Simulate noise levels (higher during the day)
        hour = time.localtime().tm_hour
        base = 60.0 if 8 <= hour <= 20 else 40.0
        self.last_value = base + (np.random.rand() * 20.0)
        self.timestamp = time.time()
        return self.last_value


class TrafficSensor(CitySensor):
    """
    Monitors traffic density (0.0 to 1.0).
    """
    def read(self) -> float:
        if self.mock_mode:
            return self.last_value
        # Simulate traffic density
        hour = time.localtime().tm_hour
        if 7 <= hour <= 9 or 16 <= hour <= 19:
            base = 0.8
        else:
            base = 0.3
        self.last_value = min(1.0, base + (np.random.rand() * 0.4 - 0.2))
        self.timestamp = time.time()
        return self.last_value


class EMFSensor(CitySensor):
    """
    Monitors Electromagnetic Field (EMF) fluctuations.
    """
    def read(self) -> float:
        if self.mock_mode:
            return self.last_value
        # Simulate EMF fluctuations (G1 storm might increase this)
        self.last_value = 50.0 + (np.random.rand() * 10.0)
        self.timestamp = time.time()
        return self.last_value


class UrbanPulse(BaseModel):
    """
    Aggregates sensor data to compute a city's Vitality Index.
    """
    city_name: str
    sensors: list[CitySensor] = Field(default_factory=list)
    vitality_index: float = 0.0

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def compute_vitality(self) -> float:
        """
        Computes the Vitality Index (0.0 to 1.0).
        High noise and traffic reduce vitality, while balanced EMF increases it.
        """
        if not self.sensors:
            return 0.0

        scores = []
        for sensor in self.sensors:
            val = sensor.read()
            if isinstance(sensor, NoiseSensor):
                # Inverse: high noise = low vitality
                score = max(0.0, 1.0 - (val / 100.0))
            elif isinstance(sensor, TrafficSensor):
                # Inverse: high traffic = low vitality
                score = 1.0 - val
            elif isinstance(sensor, EMFSensor):
                # Optimal EMF around 50-60 nT (G1 zone)
                score = 1.0 - (abs(val - 55.0) / 55.0)
            else:
                score = 0.5
            scores.append(score)

        self.vitality_index = float(np.mean(scores))
        return self.vitality_index

    def get_status_report(self) -> str:
        v = self.compute_vitality()
        status = "THRIVING" if v > 0.7 else "STABLE" if v > 0.4 else "STRESSED"
        return f"City: {self.city_name} | Vitality: {v:.2f} | Status: {status}"
