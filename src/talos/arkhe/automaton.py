"""
Arkhe(n) Automaton.
Defines autonomous agents that monitor and intervene in the hypergraph.
"""

from __future__ import annotations

import logging

import numpy as np

from talos.arkhe.error_handler import safe_operation
from talos.arkhe.neural_layer import DeepNeuralLayer


class Automaton:
    """
    Base class for Arkhe agents.
    Monitors a set of nodes and performs periodic cycles.
    """

    def __init__(self, agent_id: str, watched_nodes: list[int]):
        self.agent_id = agent_id
        self.watched_nodes = watched_nodes
        self.logger = logging.getLogger(f"arkhe.automaton.{agent_id}")

    def get_current_state(self) -> np.ndarray:
        """
        Retrieves the current coherence state of nodes.
        In a real scenario, this would query the hypergraph.
        """
        # Simulate current state for 11 subjects (hubs)
        return np.random.rand(11)

    def trigger_intervention(self, reason: str) -> None:
        """
        Executes a recovery protocol (e.g., gamma-phi pulse).
        """
        self.logger.warning(f"Intervention triggered: {reason}")
        print(f"[{self.agent_id}] Triggering intervention: {reason}")

    def cycle(self) -> None:
        """
        Periodic operational cycle.
        """
        self.logger.info("Cycle executed.")


class PredictiveAutomaton(Automaton):
    """
    An agent that uses a deep neural layer to anticipate coherence drops.
    """

    def __init__(self, agent_id: str, watched_nodes: list[int], model_id: str):
        super().__init__(agent_id, watched_nodes)
        self.neural_layer = DeepNeuralLayer.load(model_id)

    @safe_operation
    def cycle(self) -> None:
        """
        Forecasts future coherence and intervenes if a drop is predicted.
        """
        state = self.get_current_state()
        # Forecast next 6 steps
        future_c = self.neural_layer.forecast(state, steps=6)

        # Check if any future state for watched nodes falls below threshold (0.85)
        # future_c has shape (steps, output_size)
        if np.any(future_c[:, self.watched_nodes] < 0.85):
            self.trigger_intervention("Predicted coherence drop below 0.85 threshold")

        super().cycle()
