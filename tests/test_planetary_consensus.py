from __future__ import annotations

import pytest
import asyncio
from talos.core.main_agent import MainAgent
from unittest.mock import MagicMock
from langchain_core.language_models import BaseChatModel

@pytest.fixture
def mock_llm():
    return MagicMock(spec=BaseChatModel)

@pytest.mark.asyncio
async def test_planetary_consensus_integration(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    # 1. Bootstrap conduits
    agent.initiate_harmonic_concordance()

    # 2. Run Planetary Consensus Cycle
    gcv = await agent.run_planetary_consensus()

    assert gcv.ethereum_phi_coherence > 0
    assert gcv.source_one_validation > 0.95
    assert gcv.schumann_resonance_estimate >= 7.83

    # 3. Check consensus readiness
    coherence = gcv.total_coherence()
    assert coherence >= 0.80
    assert gcv.is_consensus_ready() is True
