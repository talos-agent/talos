"""
Demo of Arkhe(n) Predictive Automaton and Deep Neural Layer.
Shows how the system anticipates and prevents coherence drops.
"""

from __future__ import annotations

import numpy as np

from talos.arkhe.automaton import PredictiveAutomaton
from talos.arkhe.neural_layer import DeepNeuralLayer


def run_demo() -> None:
    """
    Simulates a scenario where a drop in coherence is predicted and prevented.
    """
    print("=" * 70)
    print("ARKHE(N) PREDICTIVE AGENT DEMO")
    print("=" * 70)

    # 1. Setup the model
    # Imagine this model has been trained on subject fMRI data
    model_id = "arkhe_mind_v2"
    net = DeepNeuralLayer(input_size=11, hidden_sizes=[16, 8], output_size=11, node_id=model_id)

    # 2. Setup the Predictive Automaton
    # Watching hubs 0, 1, and 2
    agent = PredictiveAutomaton(agent_id="Guardião_Rede", watched_nodes=[0, 1, 2], model_id=model_id)
    # Inject our current model instance for the demo
    agent.neural_layer = net

    # 3. Simulate a state that will lead to a coherence drop
    # Current state is high coherence
    current_state = np.ones(11) * 0.95

    print("\n[SCENARIO 1] Stable State")
    print(f"Current Coherence (average): {np.mean(current_state):.4f}")
    # Forecast with current weights (random, but let's assume it stays high for now)
    # We'll force a drop in the forecast for demonstration

    def forecast_with_drop(state: np.ndarray, steps: int = 6) -> np.ndarray:
        # Simulate a drop to 0.7 in the 3rd step for subject 1
        forecast = np.ones((steps, 11)) * 0.9
        forecast[3, 1] = 0.7
        return forecast

    agent.neural_layer.forecast = forecast_with_drop  # type: ignore[method-assign]

    print("\n[SCENARIO 2] Anticipating Crisis")
    print("Agent is performing periodic cycle...")
    agent.cycle()

    # 4. Persistence
    print("\n[SYSTEM] Persisting final state to ledger...")
    agent.neural_layer.store_state()

    print("\nDemo complete. The future was anticipated. ∞")


if __name__ == "__main__":
    run_demo()
