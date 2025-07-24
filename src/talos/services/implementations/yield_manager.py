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
        min_yield: float = 0.01,
        max_yield: float = 0.20,
    ):
        if min_yield <= 0 or max_yield <= 0:
            raise ValueError("Min and max yield must be positive")
        if min_yield >= max_yield:
            raise ValueError("Min yield must be less than max yield")
        
        self.dexscreener_client = dexscreener_client
        self.gecko_terminal_client = gecko_terminal_client
        self.llm_client = llm_client
        self.min_yield = min_yield
        self.max_yield = max_yield
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

        data_scores = self._calculate_data_source_scores(
            dexscreener_data, ohlcv_data, sentiment, staked_supply_percentage
        )
        logging.info(f"Data source scores: {data_scores}")
        
        weighted_apr = self._calculate_weighted_apr_recommendation(data_scores)
        logging.info(f"Weighted APR recommendation: {weighted_apr}")

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
        
        enhanced_prompt = f"{prompt}\n\nBased on weighted analysis of the data sources, the recommended APR is {weighted_apr:.4f}. Please consider this recommendation along with the raw data. The APR must be between {self.min_yield} and {self.max_yield}."
        
        response = self.llm_client.reasoning(enhanced_prompt, web_search=True)
        try:
            response_json = json.loads(response)
            llm_apr = response_json["apr"]
            explanation = response_json["explanation"]
            logging.info(f"LLM explanation: {explanation}")
        except (json.JSONDecodeError, KeyError) as e:
            logging.error(f"Failed to parse LLM response: {e}")
            logging.info("Using weighted APR recommendation as fallback")
            return max(self.min_yield, min(self.max_yield, weighted_apr))

        final_apr = max(self.min_yield, min(self.max_yield, llm_apr))
        
        if final_apr != llm_apr:
            logging.info(f"APR bounded from {llm_apr} to {final_apr} (min: {self.min_yield}, max: {self.max_yield})")
        
        return final_apr

    def get_staked_supply_percentage(self) -> float:
        return 0.45

    def _calculate_data_source_scores(self, dexscreener_data, ohlcv_data, sentiment: float, staked_supply_percentage: float) -> dict:
        scores = {}
        
        price_change = dexscreener_data.price_change_h24
        if price_change > 0.1:
            scores['price_trend'] = 0.8
        elif price_change > 0.05:
            scores['price_trend'] = 0.6
        elif price_change > -0.05:
            scores['price_trend'] = 0.5
        elif price_change > -0.1:
            scores['price_trend'] = 0.3
        else:
            scores['price_trend'] = 0.1
        
        volume = dexscreener_data.volume_h24
        if volume > 1000000:
            scores['volume_confidence'] = 0.8
        elif volume > 500000:
            scores['volume_confidence'] = 0.6
        elif volume > 100000:
            scores['volume_confidence'] = 0.4
        else:
            scores['volume_confidence'] = 0.2
        
        scores['sentiment'] = max(0.0, min(1.0, sentiment / 100.0))
        
        if staked_supply_percentage > 0.8:
            scores['supply_pressure'] = 0.2
        elif staked_supply_percentage > 0.6:
            scores['supply_pressure'] = 0.4
        elif staked_supply_percentage > 0.4:
            scores['supply_pressure'] = 0.6
        elif staked_supply_percentage > 0.2:
            scores['supply_pressure'] = 0.8
        else:
            scores['supply_pressure'] = 1.0
        
        if ohlcv_data.ohlcv_list:
            recent_ohlcv = ohlcv_data.ohlcv_list[-5:]
            if len(recent_ohlcv) >= 2:
                price_range = max(item.high for item in recent_ohlcv) - min(item.low for item in recent_ohlcv)
                avg_price = sum(item.close for item in recent_ohlcv) / len(recent_ohlcv)
                volatility = price_range / avg_price if avg_price > 0 else 0
                
                if volatility > 0.2:
                    scores['volatility'] = 0.3
                elif volatility > 0.1:
                    scores['volatility'] = 0.5
                else:
                    scores['volatility'] = 0.7
            else:
                scores['volatility'] = 0.5
        else:
            scores['volatility'] = 0.5
        
        return scores

    def _calculate_weighted_apr_recommendation(self, scores: dict) -> float:
        weights = {
            'price_trend': 0.25,
            'volume_confidence': 0.15,
            'sentiment': 0.20,
            'supply_pressure': 0.25,
            'volatility': 0.15
        }
        
        weighted_score = sum(scores[factor] * weights[factor] for factor in weights.keys())
        
        apr_recommendation = self.min_yield + (weighted_score * (self.max_yield - self.min_yield))
        
        return apr_recommendation
