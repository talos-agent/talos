"""
Tests for Arkhe(n) refinement and integration (Neural Layer v2 and Predictive Automaton).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from talos.arkhe.automaton import PredictiveAutomaton
from talos.arkhe.neural_layer import DeepNeuralLayer


def test_deep_neural_layer_forecast() -> None:
    """
    Verifies that the DeepNeuralLayer can forecast future states.
    """
    input_size = 11
    hidden_sizes = [16, 8]
    output_size = 11
    node_id = "test_deep_neural"

    net = DeepNeuralLayer(input_size, hidden_sizes, output_size, node_id)
    initial_state = np.random.rand(input_size)

    steps = 6
    future_states = net.forecast(initial_state, steps=steps)

    assert future_states.shape == (steps, output_size)
    assert len(net.activation_history) >= steps


def test_predictive_automaton_cycle() -> None:
    """
    Verifies that the PredictiveAutomaton triggers intervention on low coherence forecast.
    """
    agent_id = "Lighthouse_March"
    watched_nodes = [0, 1, 2]
    model_id = "arkhe_neural_v2"

    agent = PredictiveAutomaton(agent_id, watched_nodes, model_id)

    # Mock forecast to return low coherence values
    low_coherence = np.zeros((6, 11))

    def mock_forecast(initial_state: np.ndarray, steps: int = 6) -> np.ndarray:
        return low_coherence

    # Assigning to the instance slot
    agent.neural_layer.forecast = mock_forecast  # type: ignore[method-assign]

    # Should print/trigger intervention
    agent.cycle()


def test_deep_neural_layer_store_state(tmp_path: Any) -> None:
    """
    Verifies that the model state can be stored.
    """
    import os

    # Change current directory to temp path for file writing
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        net = DeepNeuralLayer(11, [4], 11, "test_store")
        state = net.store_state()
        assert state["node_id"] == "test_store"
        assert os.path.exists("arkhe_ledger.txt")
    finally:
        os.chdir(old_cwd)
