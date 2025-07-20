from ..tools.dexscreener import DexscreenerTool
from ..tools.twitter import TwitterTool
from ..prompts.prompt_manager import PromptManager
from ..core.main_agent import MainAgent
from ..services.proposals.models import RunParams
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
import os

class YieldManager:
    def __init__(self, dexscreener_tool: DexscreenerTool, twitter_tool: TwitterTool, prompt_manager: PromptManager):
        self.dexscreener_tool = dexscreener_tool
        self.twitter_tool = twitter_tool
        self.prompt_manager = prompt_manager
        self.agent = MainAgent(
            llm=ChatOpenAI(model="gpt-3.5-turbo", api_key=SecretStr(os.environ.get("OPENAI_API_KEY", ""))),
            tools=[dexscreener_tool, twitter_tool],
            prompts_dir="src/talos/prompts",
        )

    def adjust_apr(self) -> str:
        price = self.dexscreener_tool._run(token_address="0xdaae914e4bae2aae4f536006c353117b90fb37e3")
        sentiment = self.twitter_tool._run(tool_name="get_tweet_sentiment", search_query="Talos protocol")
        prompt = self.prompt_manager.get_prompt("yield_management")
        if prompt is None:
            raise ValueError("Yield management prompt not found")

        params = RunParams(prompt="yield_management", prompt_args={"price": price, "sentiment": sentiment})
        response = self.agent.run("", params)
        return response.answers[0]
