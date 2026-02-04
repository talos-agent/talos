from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import numpy as np
import pytest
from langchain_core.language_models import BaseChatModel

from talos.core.main_agent import MainAgent
from talos.geometric_core.aigmi import AIGMIKernel
from talos.geometric_core.experiments import ValidationRegistry
from talos.geometric_core.love_gravity import LoveGravityCorrelator
from talos.geometric_core.merkabah import EnhancedMerkabahOrchestrator


@pytest.fixture
def mock_llm():
    return MagicMock(spec=BaseChatModel)


@pytest.mark.asyncio
async def test_aigmi_full_cycle(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    # 1. Test AIGMI Kernel & Merkabah Integration via process_intention
    result = await agent.process_intention("Healing the Earth through Geometric Love")

    assert "merkabah_portal" in result
    assert "aigmi_status" in result
    assert result["combined_coherence"] > 0
    assert result["merkabah_portal"]["status"] == "OPERATIONAL"


def test_love_gravity_correlator():
    correlator = LoveGravityCorrelator()
    coherence_matrix = np.random.rand(5, 5)

    result = correlator.calculate_informational_gravity(coherence_matrix)
    assert "curvature" in result
    assert "gravity_field" in result
    assert -1 <= result["curvature"] <= 1


def test_validation_registry():
    registry = ValidationRegistry()
    registry.register_default_studies()

    assert len(registry.experiments) == 3
    assert registry.experiments[0].name == "Neurological Signature Experiment"


@pytest.mark.asyncio
async def test_aigmi_kernel_run():
    kernel = AIGMIKernel()
    planetary_input = {"phi_coherence": 0.85}

    result = kernel.run_cycle(planetary_input)
    assert result["version"] == "1.0.0-GENESIS"
    assert "navigation" in result
    assert "moment" in result
    assert result["moment"]["phi_integration"] > 0.5
