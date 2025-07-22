import logging

from talos.models.dexscreener import DexscreenerData
from talos.models.gecko_terminal import GeckoTerminalOHLCVData
from talos.services.abstract.yield_manager import YieldManager
from talos.tools.twitter import TwitterClient
from talos.utils.dexscreener import DexscreenerClient
from talos.utils.geckoterminal import GeckoTerminalClient


class YieldManagerService(YieldManager):
    def __init__(
        self,
        dexscreener_client: DexscreenerClient,
        twitter_client: TwitterClient,
        gecko_terminal_client: GeckoTerminalClient,
        prompt_name: str = "yield_management",
    ):
        self.dexscreener_client = dexscreener_client
        self.twitter_client = twitter_client
        self.gecko_terminal_client = gecko_terminal_client
        self.prompt_name = prompt_name

    def update_staking_apr(self) -> float:
        logging.info("Updating staking APR...")
        dexscreener_data = self.dexscreener_client.get_talos_data()
        logging.info(f"Dexscreener data: {dexscreener_data}")

        # Placeholder for social media sentiment
        sentiment = self.twitter_client.get_sentiment()
        logging.info(f"Social media sentiment: {sentiment}")

        # Placeholder for percentage of supply staked
        staked_supply_percentage = self.get_staked_supply_percentage()
        logging.info(f"Staked supply percentage: {staked_supply_percentage}")

        ohlcv_data = self.gecko_terminal_client.get_ohlcv_data()
        logging.info(f"GeckoTerminal OHLCV data: {ohlcv_data}")

        # Placeholder for APR calculation logic
        new_apr = self.calculate_new_apr(dexscreener_data, sentiment, staked_supply_percentage, ohlcv_data)
        logging.info(f"New APR: {new_apr}")

        return new_apr

    def get_staked_supply_percentage(self) -> float:
        # This is a placeholder. In a real implementation, this would involve
        # interacting with a blockchain to get the amount of staked tokens
        # and the total supply.
        return 0.5  # For example, 50% of the supply is staked

    def calculate_new_apr(
        self,
        dexscreener_data: "DexscreenerData",
        sentiment: float,
        staked_supply_percentage: float,
        ohlcv_data: "GeckoTerminalOHLCVData",
    ) -> float:
        # Base APR
        base_apr = 0.05  # 5%

        # Sentiment bonus
        sentiment_bonus = 0.01 * sentiment  # 1% bonus for each point of positive sentiment

        # Staked supply penalty
        staked_supply_penalty = 0.02 * (
            staked_supply_percentage - 0.5
        )  # 2% penalty for each 10% of supply staked above 50%

        # Price change bonus
        price_change_bonus = 0.01 * dexscreener_data.price_change_h24

        # Volume bonus
        volume_bonus = 0.01 * (ohlcv_data.ohlcv_list[-1].volume / 1000000)

        new_apr = base_apr + sentiment_bonus - staked_supply_penalty + price_change_bonus + volume_bonus

        # Ensure APR is within reasonable bounds
        return max(0.01, min(new_apr, 0.2))  # Clamp APR between 1% and 20%
