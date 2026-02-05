from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from langchain_core.language_models import BaseChatModel

from talos.core.main_agent import MainAgent
from talos.services.portals import IDEType


@pytest.fixture
def mock_llm():
    return MagicMock(spec=BaseChatModel)


def test_portal_integration(mock_llm):
    agent = MainAgent(model=mock_llm, prompts_dir="src/talos/prompts")

    assert agent.portal_manager is not None
    portals = agent.portal_manager.get_all_portals()

    # Check all three portals are registered
    ide_types = [p.ide_type for p in portals]
    assert IDEType.XCODE in ide_types
    assert IDEType.ANDROID_STUDIO in ide_types
    assert IDEType.VISUAL_STUDIO in ide_types

    # Check Visual Studio specifics
    vs_portal = next(p for p in portals if p.ide_type == IDEType.VISUAL_STUDIO)
    assert "C# 12.0" in vs_portal.frameworks
    assert "MAUI" in vs_portal.frameworks
    assert vs_portal.status == "Complete"
