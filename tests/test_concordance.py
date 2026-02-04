from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from langchain_core.language_models import BaseChatModel

from talos.core.main_agent import MainAgent


@pytest.fixture
def mock_llm():
    return MagicMock(spec=BaseChatModel)


def test_harmonic_concordance_bootstrap(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    # 1. Initiate Bootstrap
    result = agent.initiate_harmonic_concordance()
    assert "CIRCUIT_CLOSED" in result
    assert len(agent.concordance_service.conduits) == 3

    # 2. Run Federated Round
    gcv = agent.concordance_service.run_federated_round()
    assert gcv.schumann_resonance_estimate >= 7.83
    # collective_emotion_scalar is now a tuple
    assert gcv.collective_emotion_scalar[0] == 0.85
    assert gcv.timestamp > 0
