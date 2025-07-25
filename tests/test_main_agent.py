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
    """
    Returns a mock of the BaseChatModel.
    """
    return MagicMock(spec=BaseChatModel)


def test_main_agent_initialization(mock_model: BaseChatModel) -> None:
    """
    Tests that the MainAgent can be initialized without errors.
    """
    with (
        patch("talos.core.main_agent.FilePromptManager") as mock_file_prompt_manager,
        patch("talos.core.main_agent.Hypervisor") as mock_hypervisor,
        patch.dict(
            "os.environ",
            {
                "GITHUB_API_TOKEN": "test_token",
                "OPENAI_API_KEY": "test_key",
                "TWITTER_BEARER_TOKEN": "test_twitter_token",
            },
        ),
        patch("os.environ.get") as mock_os_get,
        patch("ssl.create_default_context", return_value=MagicMock()),
        patch("tweepy.Client"),
        patch("langchain_openai.ChatOpenAI"),
    ):
        mock_os_get.side_effect = lambda key, default=None: {
            "GITHUB_API_TOKEN": "test_token",
            "OPENAI_API_KEY": "test_key",
            "TWITTER_BEARER_TOKEN": "test_twitter_token",
        }.get(key, default)
        mock_prompt_manager = MagicMock(spec=FilePromptManager)
        mock_prompt_manager.get_prompt.return_value = Prompt(
            name="main_agent_prompt",
            template="You are a helpful assistant.",
            input_variables=[],
        )
        mock_file_prompt_manager.return_value = mock_prompt_manager
        mock_hypervisor.return_value = MagicMock(spec=Hypervisor)
        from talos.skills.proposals import ProposalsSkill

        agent = MainAgent(
            model=mock_model,
            prompts_dir="",
            prompt_manager=mock_prompt_manager,
            schema=None,
            router=Router(
                services=[],
                skills=[ProposalsSkill(llm=mock_model)],
            ),
        )
        assert agent is not None
        assert agent.model == mock_model
        assert agent.prompt_manager == mock_prompt_manager
        assert agent.router is not None
        assert agent.supervisor is not None
        assert agent.tool_manager is not None
        assert len(agent.tool_manager.tools) > 0
