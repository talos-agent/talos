import json
import logging

from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.yield_manager import YieldManager
from talos.tools.twitter_client import TweepyClient
from talos.utils.dexscreener import DexscreenerClient
from talos.utils.geckoterminal import GeckoTerminalClient
from talos.utils.llm import LLMClient


class YieldManagerService(YieldManager):
    def __init__(
        self,
        dexscreener_client: DexscreenerClient,
        gecko_terminal_client: GeckoTerminalClient,
        llm_client: LLMClient,
        prompt_name: str = "yield_management",
    ):
        self.dexscreener_client = dexscreener_client
        self.gecko_terminal_client = gecko_terminal_client
        self.llm_client = llm_client
        self.twitter_client = TweepyClient()
        self.prompt_manager = FilePromptManager("src/talos/prompts")
        self.prompt = self.prompt_manager.get_prompt(prompt_name)

    def update_staking_apr(self, sentiment: float, sentiment_report: str) -> float:
        logging.info("Updating staking APR...")
        dexscreener_data = self.dexscreener_client.get_talos_data()
        logging.info(f"Dexscreener data: {dexscreener_data}")

        logging.info(f"Social media sentiment: {sentiment}")
        logging.info(f"Sentiment report: {sentiment_report}")

        staked_supply_percentage = self.get_staked_supply_percentage()
        logging.info(f"Staked supply percentage: {staked_supply_percentage}")

        ohlcv_data = self.gecko_terminal_client.get_ohlcv_data()
        logging.info(f"GeckoTerminal OHLCV data: {ohlcv_data}")

        if not self.prompt:
            raise ValueError("Prompt not found")

        prompt = self.prompt.format(
            price=dexscreener_data.price_usd,
            change=dexscreener_data.price_change_h24,
            volume=dexscreener_data.volume_h24,
            sentiment=sentiment,
            staked_supply_percentage=staked_supply_percentage,
            ohlcv_data=ohlcv_data.model_dump_json(),
        )
        response = self.llm_client.reasoning(prompt, web_search=True)
        try:
            response_json = json.loads(response)
            new_apr = response_json["apr"]
            explanation = response_json["explanation"]
            logging.info(f"LLM explanation: {explanation}")
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to parse LLM response: {e}")
            raise

        return new_apr

    def get_staked_supply_percentage(self) -> float:
        return 0.5
