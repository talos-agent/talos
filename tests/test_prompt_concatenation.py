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


def test_prompt_concatenation(mock_model: BaseChatModel) -> None:
    """
    Tests that the MainAgent can be initialized with a concatenated prompt.
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

        # Create a mock FilePromptManager
        with patch("os.listdir", return_value=[]):
            mock_prompt_manager = FilePromptManager(prompts_dir="dummy_dir")

        # Add mock prompts
        mock_prompt_manager.prompts = {
            "main_agent_prompt": Prompt(
                name="main_agent_prompt",
                template="This is the main prompt.",
                input_variables=[],
            ),
            "general_agent_prompt": Prompt(
                name="general_agent_prompt",
                template="This is the general prompt.",
                input_variables=["time"],
            ),
        }

        mock_file_prompt_manager.return_value = mock_prompt_manager
        mock_hypervisor.return_value = MagicMock(spec=Hypervisor)

        from talos.skills.proposals import ProposalsSkill

        MainAgent(
            model=mock_model,
            prompts_dir="",
            prompt_manager=mock_prompt_manager,
            schema=None,
            router=Router(
                services=[],
                skills=[ProposalsSkill(llm=mock_model)],
            ),
        )
