"""
Arkhe(n) + RFID: Physical Identity Modeling in the Hypergraph.
Each RFID tag is a node. Each reading is a handover.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

import numpy as np


class RFIDTag:
    """
    Represents an RFID tag as a node in the Arkhe hypergraph.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(
        self, tag_id: str, object_type: str, metadata: dict[str, Any] | None = None
    ):
        self.tag_id = tag_id
        self.object_type = object_type
        self.creation_time = datetime.now()
        self.handovers: list[dict[str, Any]] = []
        self.coherence_history: list[dict[str, Any]] = []
        self.metadata = metadata or {}
        self.location: str | None = None
        self.gps_coords: tuple[float, float] | None = None
        self.last_seen: datetime | None = None
        self.status: str = "ATIVO"

    def read(
        self,
        reader_id: str,
        location: str,
        gps: tuple[float, float] | None = None,
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Registers a tag reading (handover)."""
        if timestamp is None:
            timestamp = datetime.now()

        delta = 0.0
        if self.last_seen:
            delta = (timestamp - self.last_seen).total_seconds()

        handover = {
            "timestamp": timestamp.isoformat(),
            "reader_id": reader_id,
            "location": location,
            "gps": gps,
            "delta_seconds": delta,
            "handover_number": len(self.handovers) + 1,
        }

        self.handovers.append(handover)
        self.location = location
        self.gps_coords = gps
        self.last_seen = timestamp

        self._update_coherence()
        return handover

    def _update_coherence(self) -> tuple[float, float]:
        """Calculates C and F based on reading regularity."""
        if len(self.handovers) < 2:
            coherence = 0.0
        else:
            intervals = [
                h["delta_seconds"] for h in self.handovers[1:] if h["delta_seconds"] > 0
            ]
            if not intervals:
                coherence = 0.0
            else:
                mean_interval = np.mean(intervals)
                std_interval = np.std(intervals)
                if mean_interval > 0:
                    cov = std_interval / mean_interval
                    coherence = 1.0 / (1.0 + cov)
                else:
                    coherence = 0.0

        fluctuation = 1.0 - coherence
        self.coherence_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "C": coherence,
                "F": fluctuation,
                "handover_number": len(self.handovers),
            }
        )
        return float(coherence), float(fluctuation)

    def get_effective_dimension(self, lambda_reg: float = 1.0) -> float:
        """Calculates the effective dimension d_lambda of the tag."""
        if len(self.handovers) < 2:
            return 0.0

        intervals = [
            h["delta_seconds"] for h in self.handovers[1:] if h["delta_seconds"] > 0
        ]
        if not intervals:
            return 0.0

        eigenvalues = np.array(intervals) / np.mean(intervals)
        contributions = eigenvalues / (eigenvalues + lambda_reg)
        return float(np.sum(contributions))

    def get_path_history(self) -> list[str]:
        """Returns the sequence of locations (object geodesic)."""
        return [h["location"] for h in self.handovers]

    def verify_conservation(self, tolerance: float = 1e-6) -> bool:
        """Verifies if C + F = 1 holds."""
        if not self.coherence_history:
            return True
        last = self.coherence_history[-1]
        return bool(abs(last["C"] + last["F"] - 1.0) < tolerance)

    def to_json(self) -> str:
        """Serializes the tag to JSON."""
        data = {
            "tag_id": self.tag_id,
            "object_type": self.object_type,
            "creation_time": self.creation_time.isoformat(),
            "handovers": self.handovers,
            "coherence_history": self.coherence_history,
            "metadata": self.metadata,
            "location": self.location,
            "gps": self.gps_coords,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "status": self.status,
            "satoshi": len(self.handovers),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


class RFIDHypergraph:
    """
    RFID Hypergraph: contains all nodes and manages their connections.
    """

    def __init__(self) -> None:
        self.tags: dict[str, RFIDTag] = {}
        self.readers: dict[str, list[str]] = {}
        self.locations: dict[str, list[str]] = {}

    def add_tag(self, tag: RFIDTag) -> None:
        """Adds a new tag to the hypergraph."""
        self.tags[tag.tag_id] = tag

    def register_reading(
        self,
        tag_id: str,
        reader_id: str,
        location: str,
        gps: tuple[float, float] | None = None,
        timestamp: datetime | None = None,
    ) -> dict[str, Any]:
        """Registers a reading and updates indices."""
        if tag_id not in self.tags:
            raise ValueError(f"Tag {tag_id} not found")

        tag = self.tags[tag_id]
        handover = tag.read(reader_id, location, gps, timestamp)

        if reader_id not in self.readers:
            self.readers[reader_id] = []
        self.readers[reader_id].append(tag_id)

        if location not in self.locations:
            self.locations[location] = []
        self.locations[location].append(tag_id)

        return handover

    def identify_anomalies(self, threshold: float = 0.3) -> list[str]:
        """Identifies tags with low coherence (high fluctuation)."""
        anomalies = []
        for tag_id, tag in self.tags.items():
            if len(tag.handovers) >= 2 and tag.coherence_history[-1]["C"] < threshold:
                anomalies.append(tag_id)
        return anomalies

    def apply_protocol(self, tag_id: str, protocol: str) -> str:
        """Applies a specific handling protocol to a tag."""
        if tag_id not in self.tags:
            return "TAG_NOT_FOUND"

        tag = self.tags[tag_id]
        if protocol == "RESGATE":
            tag.status = "EM_RESGATE"
        elif protocol == "FANTASMA":
            tag.status = "MODO_FANTASMA"
        elif protocol == "SACRIFICIO":
            tag.status = "SACRIFICADO"
        elif protocol == "INTEGRACAO":
            tag.status = "INTEGRADO"
        else:
            return "INVALID_PROTOCOL"

        return tag.status


def simulate_supply_chain() -> RFIDHypergraph:
    """Simulates a simple supply chain with RFID tags."""
    hypergraph = RFIDHypergraph()
    prod = RFIDTag("RFID_001", "smartphone")
    hypergraph.add_tag(prod)

    base_time = datetime.now()
    timeline = [
        ("leitor_01", "Fabrica", ( -23.55, -46.63), 0),
        ("leitor_02", "CD", (-23.56, -46.64), 3600),
        ("leitor_03", "Loja", (-23.57, -46.65), 7200),
    ]

    for reader, loc, gps, sec in timeline:
        ts = base_time + timedelta(seconds=sec)
        hypergraph.register_reading("RFID_001", reader, loc, gps, ts)

    return hypergraph
