from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from langchain_core.language_models import BaseChatModel

from talos.core.main_agent import MainAgent
from talos.core.router import Router
from talos.hypervisor.hypervisor import Hypervisor
from talos.prompts.prompt import Prompt
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager


@pytest.fixture
def mock_model() -> BaseChatModel:
    return MagicMock(spec=BaseChatModel)


def test_main_agent_initialization(mock_model: BaseChatModel) -> None:
    """
    Tests that the MainAgent can be initialized without errors.
    """
    with (
        patch("talos.core.main_agent.FilePromptManager") as mock_file_prompt_manager,
        patch("talos.core.main_agent.Hypervisor") as mock_hypervisor,
        patch("os.environ.get") as mock_os_get,
        patch("ssl.create_default_context", return_value=MagicMock()),
    ):
        mock_os_get.side_effect = lambda key, default=None: {
            "GITHUB_TOKEN": "test_token",
            "GITHUB_API_TOKEN": "test_token",
        }.get(key, default)
        mock_prompt_manager = MagicMock(spec=FilePromptManager)
        mock_prompt_manager.get_prompt.return_value = Prompt(
            name="main_agent_prompt",
            template="You are a helpful assistant.",
            input_variables=[],
        )
        mock_file_prompt_manager.return_value = mock_prompt_manager
        mock_hypervisor.return_value = MagicMock(spec=Hypervisor)
        agent = MainAgent(
            model=mock_model,
            prompts_dir="",
            prompt_manager=mock_prompt_manager,
            schema=None,
            router=Router(services=[]),
        )
        assert agent is not None
        mock_prompt_manager.get_prompt.assert_called_with("main_agent_prompt")
