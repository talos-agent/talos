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


@pytest.mark.asyncio
async def test_process_intention(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    result = await agent.process_intention("Manifest peace and global harmony")

    assert "intention" in result
    assert result["intention"] == "Manifest peace and global harmony"
    assert "field_coherence" in result
    assert "earth_coherence" in result
    assert "geometric_insights" in result
    assert result["combined_coherence"] > 0
