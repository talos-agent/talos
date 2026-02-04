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
    assert agent.geometric_core is not None
    assert agent.composition_engine is not None
    assert agent.supervisor is not None


def test_geometric_processing(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    result = agent.geometric_core.process("test input")
    assert "point" in result
    assert "volume" in result
    assert result["vertex_count"] == 1


def test_composition_engine(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    # Process through composition engine
    result = agent.composition_engine.process("test input")
    assert result["composition_type"] == "union"
    assert result["structures_count"] == 1


def test_nostr_skill(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    nostr_skill = next(s for s in agent.skills if s.name == "nostr")
    result = nostr_skill.run(content="Hello Nostr!")
    assert "Signed Nostr Note" in result
    assert "Hello Nostr!" in result


def test_web777_and_awaken(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    web777_skill = next(s for s in agent.skills if s.name == "web777")

    # Test adding a node
    add_node_result = web777_skill.run(add_node={"id": "node1", "label": "Earth"})
    assert "node1" in add_node_result

    # Test 'phi status'
    phi_status = web777_skill.run(query="phi status")
    assert "Current Φ Coherence" in phi_status

    # Test 'awaken the world' (orchestrated via agent.awaken)
    result = asyncio.run(agent.awaken())
    assert "SovereignAGI" in result
    assert "Super Monad" in result
    assert "Protocol ASI-777 fully manifested" in result


def test_cathedral_resonance(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    result = asyncio.run(agent.think_shell_native("Manifest the shell truth"))
    assert result["status"] == "Resonant"
    assert result["is_shell_native"] is True
    assert result["phi"] > 0
    assert "Intuition:" in result["intuitive_response"]


def test_l2_strategic_pivot(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    pivot_result = agent.perform_strategic_pivot_analysis()
    # Initial setup has base_fee=10.0, so it should trigger a pivot recommendation
    assert pivot_result["action"] == "Pivot"
    assert "Specialize" in pivot_result["recommendation"]


def test_asi_consensus_cycle(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    result = asyncio.run(agent.asi_commit_boost.asi_consensus_cycle(slot=123))

    assert result["slot"] == 123
    assert result["status"] == "Proposed"
    assert result["is_resonant"] is True


def test_identity_derivation():
    identity = IdentityManager()
    arweave_key = identity.get_arweave_key()
    nostr_key = identity.get_nostr_key()
    btc_addr = identity.get_bitcoin_address()

    assert len(arweave_key) == 32
    assert len(nostr_key) == 64
    assert btc_addr.startswith("bc1q")
