import unittest
from unittest.mock import MagicMock

from talos.services.implementations.yield_manager import YieldManagerService


class TestYieldManagerService(unittest.TestCase):
    def test_update_staking_apr(self):
        dexscreener_client = MagicMock()
        twitter_client = MagicMock()

        from talos.models.dexscreener import DexscreenerData

        dexscreener_client.get_talos_data.return_value = DexscreenerData(
            priceUsd=1.0,
            priceChange=0.1,
            volume=1000000,
        )
        twitter_client.get_sentiment.return_value = 1.0

        gecko_terminal_client = MagicMock()
        from talos.models.gecko_terminal import OHLCV, GeckoTerminalOHLCVData

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
        yield_manager = YieldManagerService(dexscreener_client, twitter_client, gecko_terminal_client)
        yield_manager.get_staked_supply_percentage = MagicMock(return_value=0.6)

        new_apr = yield_manager.update_staking_apr()

        self.assertIsInstance(new_apr, float)
        self.assertGreaterEqual(new_apr, 0.01)
        self.assertLessEqual(new_apr, 0.2)


if __name__ == "__main__":
    unittest.main()
