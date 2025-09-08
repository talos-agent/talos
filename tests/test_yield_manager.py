import json
import unittest
from unittest.mock import MagicMock, patch

from talos.models.dexscreener import DexscreenerData
from talos.models.gecko_terminal import OHLCV, GeckoTerminalOHLCVData
from talos.services.implementations.yield_manager import YieldManagerService


class TestYieldManagerService(unittest.TestCase):
    @patch("talos.services.implementations.yield_manager.TweepyClient")
    def test_update_staking_apr(self, mock_tweepy_client):
        dexscreener_client = MagicMock()
        gecko_terminal_client = MagicMock()
        llm_client = MagicMock()

        dexscreener_client.get_talos_data.return_value = DexscreenerData(
            priceUsd=1.0,
            priceChange=0.1,
            volume=1000000,
        )
        gecko_terminal_client.get_ohlcv_data.return_value = GeckoTerminalOHLCVData(
            ohlcv_list=[
                OHLCV(
                    timestamp=1672531200,
                    open=0.1,
                    high=0.11,
                    low=0.09,
                    close=0.1,
                    volume=1000000,
                )
            ]
        )
        llm_client.reasoning.return_value = json.dumps(
            {"apr": 0.15, "explanation": "The APR has been updated based on market conditions."}
        )

        yield_manager = YieldManagerService(dexscreener_client, gecko_terminal_client, llm_client)
        yield_manager.get_staked_supply_percentage = MagicMock(return_value=0.6)

        new_apr = yield_manager.update_staking_apr(75.0, "A report")

        self.assertIsInstance(new_apr, float)
        self.assertEqual(new_apr, 0.15)

    @patch("talos.services.implementations.yield_manager.TweepyClient")
    def test_min_max_yield_validation(self, mock_tweepy_client):
        dexscreener_client = MagicMock()
        gecko_terminal_client = MagicMock()
        llm_client = MagicMock()

        with self.assertRaises(ValueError):
            YieldManagerService(dexscreener_client, gecko_terminal_client, llm_client, min_yield=-0.01)

        with self.assertRaises(ValueError):
            YieldManagerService(dexscreener_client, gecko_terminal_client, llm_client, min_yield=0.2, max_yield=0.1)

    @patch("talos.services.implementations.yield_manager.TweepyClient")
    def test_apr_bounds_enforcement(self, mock_tweepy_client):
        dexscreener_client = MagicMock()
        gecko_terminal_client = MagicMock()
        llm_client = MagicMock()

        dexscreener_client.get_talos_data.return_value = DexscreenerData(
            priceUsd=1.0,
            priceChange=0.1,
            volume=1000000,
        )
        gecko_terminal_client.get_ohlcv_data.return_value = GeckoTerminalOHLCVData(ohlcv_list=[])

        llm_client.reasoning.return_value = json.dumps({"apr": 0.25, "explanation": "High APR recommendation"})

        yield_manager = YieldManagerService(
            dexscreener_client, gecko_terminal_client, llm_client, min_yield=0.05, max_yield=0.20
        )
        yield_manager.get_staked_supply_percentage = MagicMock(return_value=0.5)

        new_apr = yield_manager.update_staking_apr(75.0, "A report")
        self.assertEqual(new_apr, 0.20)

        llm_client.reasoning.return_value = json.dumps({"apr": 0.01, "explanation": "Low APR recommendation"})

        new_apr = yield_manager.update_staking_apr(75.0, "A report")
        self.assertEqual(new_apr, 0.05)


if __name__ == "__main__":
    unittest.main()
