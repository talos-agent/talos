from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.language_models import BaseChatModel
from talos.core.main_agent import MainAgent
from talos.prompts.prompt import Prompt
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.core.router import Router


@pytest.fixture
def mock_model() -> BaseChatModel:
    return MagicMock(spec=BaseChatModel)


@pytest.fixture
def mock_prompt_manager() -> FilePromptManager:
    mock = MagicMock(spec=FilePromptManager)
    mock.get_prompt.return_value = Prompt(
        name="main_agent_prompt",
        template="You are a helpful assistant.",
        input_variables=[],
    )
    return mock


def test_main_agent_initialization(
    mock_model: BaseChatModel, mock_prompt_manager: FilePromptManager
) -> None:
    """
    Tests that the MainAgent can be initialized without errors.
    """
    with patch(
        "talos.prompts.prompt_managers.file_prompt_manager.FilePromptManager.load_prompts"
    ) as mock_load_prompts:
        mock_load_prompts.return_value = None
        agent = MainAgent(
            model=mock_model,
            prompts_dir="",
            prompt_manager=mock_prompt_manager,
            schema=None,
            router=Router(services=[]),
        )
        assert agent is not None
        mock_prompt_manager.get_prompt.assert_called_with("main_agent_prompt")
