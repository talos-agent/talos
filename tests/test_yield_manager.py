from talos.services.yield_manager import YieldManager
from talos.tools.dexscreener import DexscreenerTool
from talos.tools.twitter import TwitterTool
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.proposals.models import QueryResponse
from unittest.mock import MagicMock, patch
import os

@patch.dict(os.environ, {"OPENAI_API_KEY": "test", "GITHUB_TOKEN": "test"})
def test_yield_manager():
    dexscreener_tool = MagicMock(spec=DexscreenerTool)
    dexscreener_tool.name = "dexscreener_tool"
    dexscreener_tool._run.return_value = "$1.23"
    twitter_tool = MagicMock(spec=TwitterTool)
    twitter_tool.name = "twitter_tool"
    twitter_tool._run.return_value = {"positive": 10, "negative": 1, "neutral": 5}
    prompt_manager = FilePromptManager(prompts_dir="src/talos/prompts")
    yield_manager = YieldManager(dexscreener_tool, twitter_tool, prompt_manager)
    yield_manager.agent.run = MagicMock(return_value=QueryResponse(answers=["The APR should be increased to 5%."]))
    response = yield_manager.adjust_apr()
    assert response == "The APR should be increased to 5%."
    dexscreener_tool._run.assert_called_once_with(token_address="0xdaae914e4bae2aae4f536006c353117b90fb37e3")
    twitter_tool._run.assert_called_once_with(tool_name="get_tweet_sentiment", search_query="Talos protocol")
    yield_manager.agent.run.assert_called_once()
