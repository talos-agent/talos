from __future__ import annotations

import os
import pytest
from talos.core.main_agent import MainAgent
from unittest.mock import MagicMock, patch
from langchain_core.language_models import BaseChatModel

@pytest.fixture
def mock_llm():
    return MagicMock(spec=BaseChatModel)

def test_harmonic_concordance_bootstrap(mock_llm):
    # Set dummy API key to avoid OpenAI errors during initialization
    with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-dummy"}):
        # We still need to mock the actual calls if they happen,
        # but here we just want to avoid the init error.
        with patch("langchain_openai.OpenAIEmbeddings") as mock_embeddings:
            mock_embeddings.return_value = MagicMock()

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
