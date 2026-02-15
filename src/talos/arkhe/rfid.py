from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np


class RFIDTag:
    """
    Representa uma tag RFID como um nó no hipergrafo Arkhe.
    """

    def __init__(self, tag_id: str, object_type: str, metadata: dict | None = None):
        self.tag_id = tag_id
        self.object_type = object_type
        self.creation_time = datetime.now()
        self.handovers: list[dict] = []
        self.coherence_history: list[dict] = []
        self.metadata = metadata or {}
        self._current_location: str | None = None
        self._current_coords: tuple[float, float] | None = None
        self._last_seen: datetime | None = None
        self.status = "active"  # active, divergent, quarantined, sacrificed

    def read(
        self,
        reader_id: str,
        location: str,
        timestamp: Optional[datetime] = None,
        coords: Optional[tuple[float, float]] = None,
    ) -> dict:
        """
        Registra uma leitura (handover) da tag.
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Calcular intervalo desde última leitura
        delta = 0.0
        if self._last_seen:
            delta = (timestamp - self._last_seen).total_seconds()

        handover = {
            "timestamp": timestamp.isoformat(),
            "reader_id": reader_id,
            "location": location,
            "coords": coords,
            "delta_seconds": delta,
            "handover_number": len(self.handovers) + 1,
            "status_at_reading": self.status,
        }

        self.handovers.append(handover)
        self._current_location = location
        self._current_coords = coords
        self._last_seen = timestamp

        # Atualizar coerência (C) baseada na regularidade das leituras
        self._update_coherence()

        return handover

    def diverge(self, reason: str = "anomaly") -> None:
        """
        Marca o nó como divergente.
        """
        self.status = "divergent"
        if "divergence_reasons" not in self.metadata:
            self.metadata["divergence_reasons"] = []
        self.metadata["divergence_reasons"].append(
            {"timestamp": datetime.now().isoformat(), "reason": reason}
        )

    def _update_coherence(self) -> tuple[float, float]:
        """
        Calcula a coerência C da tag baseado na regularidade temporal das leituras.
        """
        if len(self.handovers) < 2:
            c_val = 0.0  # Poucos dados, coerência indefinida
        else:
            # Extrair intervalos
            intervals = [
                h["delta_seconds"] for h in self.handovers[1:] if h["delta_seconds"] > 0
            ]
            if not intervals:
                c_val = 0.0
            else:
                # Coerência baseada na regularidade (inverso do coeficiente de variação)
                mean_interval = np.mean(intervals)
                std_interval = np.std(intervals)
                if mean_interval > 0:
                    cv = std_interval / mean_interval
                    # Normalizar: cv=0 → C=1; cv→∞ → C→0
                    c_val = 1.0 / (1.0 + cv)
                else:
                    c_val = 0.0

        f_val = 1.0 - c_val  # Flutuação
        self.coherence_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "C": c_val,
                "F": f_val,
                "handover_number": len(self.handovers),
            }
        )

        return float(c_val), float(f_val)

    def get_effective_dimension(self, lambda_reg: float = 1.0) -> float:
        """
        Calcula a dimensão efetiva d_λ da tag baseada em seu histórico.
        """
        if len(self.handovers) < 2:
            return 0.0

        intervals = [
            h["delta_seconds"] for h in self.handovers[1:] if h["delta_seconds"] > 0
        ]
        if not intervals:
            return 0.0

        # "Autovalores" simulados como os intervalos normalizados
        eigenvalues = np.array(intervals) / np.mean(intervals)
        contributions = eigenvalues / (eigenvalues + lambda_reg)
        return float(np.sum(contributions))

    def get_path_history(self) -> List[str]:
        """Retorna a sequência de localizações (geodésica do objeto)."""
        return [h["location"] for h in self.handovers]

    def verify_conservation(self, tolerance: float = 1e-6) -> bool:
        """
        Verifica se C + F = 1 se mantém no último handover.
        """
        if not self.coherence_history:
            return True
        last = self.coherence_history[-1]
        return abs(last["C"] + last["F"] - 1.0) < tolerance

    def to_json(self) -> str:
        """Serializa a tag para JSON (formato de exportação)."""
        data = {
            "tag_id": self.tag_id,
            "object_type": self.object_type,
            "creation_time": self.creation_time.isoformat(),
            "handovers": self.handovers,
            "coherence_history": self.coherence_history,
            "metadata": self.metadata,
            "current_location": self._current_location,
            "current_coords": self._current_coords,
            "last_seen": self._last_seen.isoformat() if self._last_seen else None,
            "status": self.status,
            "satoshi": len(self.handovers),
        }
        return json.dumps(data, indent=2, ensure_ascii=False)


class RFIDHypergraph:
    """
    Hipergrafo de tags RFID.
    """

    def __init__(self) -> None:
        self.tags: Dict[str, RFIDTag] = {}
        self.readers: Dict[str, List[str]] = {}
        self.locations: Dict[str, List[str]] = {}

    def add_tag(self, tag: RFIDTag) -> None:
        """Adiciona uma nova tag ao hipergrafo."""
        self.tags[tag.tag_id] = tag

    def register_reading(
        self,
        tag_id: str,
        reader_id: str,
        location: str,
        timestamp: Optional[datetime] = None,
        coords: Optional[tuple[float, float]] = None,
    ) -> dict:
        """
        Registra uma leitura, atualizando todos os índices.
        """
        if tag_id not in self.tags:
            raise ValueError(f"Tag {tag_id} não encontrada")

        tag = self.tags[tag_id]
        handover = tag.read(reader_id, location, timestamp, coords)

        # Atualizar índices
        if reader_id not in self.readers:
            self.readers[reader_id] = []
        self.readers[reader_id].append(tag_id)

        if location not in self.locations:
            self.locations[location] = []
        self.locations[location].append(tag_id)

        return handover

    def protocol_resgate(self, tag_id: str) -> str:
        """Protocolo RESGATE (Converge): Força descarte/recuperação."""
        if tag_id not in self.tags:
            return "Tag not found"
        tag = self.tags[tag_id]
        tag.status = "quarantined"
        return f"Protocol RESGATE activated for {tag_id}. Node quarantined."

    def protocol_fantasma(self, tag_id: str) -> str:
        """Protocolo FANTASMA (Observe): Vigilância silenciosa."""
        if tag_id not in self.tags:
            return "Tag not found"
        tag = self.tags[tag_id]
        # Status remains divergent or active but we flag it for observation in metadata
        tag.metadata["observation_mode"] = True
        return f"Protocol FANTASMA activated for {tag_id}. Silent observation active."

    def protocol_sacrificio(self, tag_id: str) -> str:
        """Protocolo SACRIFÍCIO (Wipe): Autodestruição lógica."""
        if tag_id not in self.tags:
            return "Tag not found"
        tag = self.tags[tag_id]
        tag.status = "sacrificed"
        tag.metadata = {"death_timestamp": datetime.now().isoformat()}
        return f"Protocol SACRIFÍCIO activated for {tag_id}. Node logically destroyed."

    def protocol_integracao(self, tag_id: str) -> str:
        """Protocolo INTEGRAÇÃO (Accept): Aceita entropia como parte do sistema."""
        if tag_id not in self.tags:
            return "Tag not found"
        tag = self.tags[tag_id]
        tag.status = "active"
        tag.metadata["integrated_entropy"] = True
        return f"Protocol INTEGRAÇÃO activated for {tag_id}. Entropy accepted as identity."

    def query_tags_at_location(self, location: str) -> List[RFIDTag]:
        """Retorna todas as tags atualmente em uma localização."""
        tag_ids = self.locations.get(location, [])
        return [self.tags[tid] for tid in tag_ids if tid in self.tags]

    def compute_system_coherence(self) -> float:
        """
        Calcula a coerência média do sistema (C_total).
        """
        if not self.tags:
            return 0.0

        c_vals = [
            tag.coherence_history[-1]["C"]
            for tag in self.tags.values()
            if tag.coherence_history
        ]
        return float(np.mean(c_vals)) if c_vals else 0.0

    def compute_system_effective_dimension(self, lambda_reg: float = 1.0) -> float:
        """
        Dimensão efetiva total do sistema.
        """
        return sum(tag.get_effective_dimension(lambda_reg) for tag in self.tags.values())

    def identify_anomalies(self, threshold: float = 0.3) -> List[str]:
        """
        Identifica tags com baixa coerência (alta flutuação).
        """
        anomalies = []
        for tag_id, tag in self.tags.items():
            if tag.coherence_history and tag.coherence_history[-1]["C"] < threshold:
                anomalies.append(tag_id)
        return anomalies
