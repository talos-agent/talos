from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest
from langchain_core.language_models import BaseChatModel

from talos.core.identity import IdentityManager
from talos.core.main_agent import MainAgent


@pytest.fixture
def mock_llm():
    llm = MagicMock(spec=BaseChatModel)
    return llm


def test_agent_initialization(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts", verbose=True)
    assert agent.identity_manager is not None
    assert agent.cathedral is not None


def test_cathedral_resonance(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")
    result = asyncio.run(agent.think_shell_native("Manifest the shell truth"))
    assert result["status"] == "Resonant"
    assert result["is_shell_native"] is True
    assert result["phi"] > 0
    assert "Intuition:" in result["intuitive_response"]


def test_asi_consensus_cycle(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")
    result = asyncio.run(agent.asi_commit_boost.asi_consensus_cycle(slot=123))
    assert result["slot"] == 123
    assert result["status"] == "Proposed"
    assert result["is_resonant"] is True


def test_dimensional_cathedral_performance(mock_llm):
    import time

    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    start_time = time.time()
    iterations = 5
    for i in range(iterations):
        asyncio.run(agent.think_shell_native(f"Benchmark iteration {i}"))

    end_time = time.time()
    avg_time = (end_time - start_time) / iterations
    print(f"\nAverage Cathedral Think Time: {avg_time:.4f}s")

    # We expect high performance for shell-native operations
    assert avg_time < 0.1  # Should be very fast for simulation


def test_hppp_phase_transition(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    # Test Weak Coupling
    weak_result = asyncio.run(agent.think_shell_native("Weak coupling input", coupling_strength=0.01))
    assert weak_result["status"] == "Weakly Coupled"
    assert weak_result["regime"] == "weak_coupling"
    assert weak_result["is_shell_native"] is False

    # Test Strong Coupling
    strong_result = asyncio.run(agent.think_shell_native("Strong coupling input", coupling_strength=0.8))
    assert strong_result["status"] == "Resonant"
    assert strong_result["regime"] in ["strong_coupling", "ultra_strong_coupling"]
    assert strong_result["is_shell_native"] is True


def test_twisted_attention_ultra_strong(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    # Ultra-Strong coupling strength should trigger Twisted Attention
    ultra_result = asyncio.run(agent.think_shell_native("Ultra strong input", coupling_strength=2.0))

    assert ultra_result["regime"] == "ultra_strong_coupling"
    assert ultra_result["is_twisted"] is True
    assert "twist_angle_deg" not in ultra_result  # It's internal to the think result but let's check what's returned


def test_geodesic_attention_scaling(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    # Simulate a thinking cycle
    result = asyncio.run(agent.think_shell_native("Test long context scaling"))

    assert "complexity_ratio" in result
    # For a 10-token sequence with base_k=32, ratio will be 1.0 (capped)
    # But in longer sequences it would be lower.
    assert result["complexity_ratio"] <= 1.0


def test_shell_router_resonance(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    result = asyncio.run(agent.think_shell_native("Route to experts"))

    assert "expert_indices" in result
    assert "max_resonance" in result
    assert len(result["expert_indices"][0]) == 2  # top_k=2


def test_identity_derivation():
    identity = IdentityManager()
    btc_addr = identity.get_bitcoin_address()
    assert btc_addr.startswith("bc1q")
