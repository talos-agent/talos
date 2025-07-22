import requests

from talos.models.gecko_terminal import OHLCV, GeckoTerminalOHLCVData


class GeckoTerminalClient:
    def __init__(self, network: str = "arbitrum", pool_address: str = "0xdaAe914e4Bae2AAe4f536006C353117B90Fb37e3"):
        self.network = network
        self.pool_address = pool_address

    def get_ohlcv_data(self, timeframe: str = "hour") -> GeckoTerminalOHLCVData:
        """Gets the OHLCV data for a token from geckoterminal.com"""
        url = (
            f"https://api.geckoterminal.com/api/v2/networks/{self.network}/pools/{self.pool_address}/ohlcv/{timeframe}"
        )
        response = requests.get(url, headers={"accept": "application/json"})
        response.raise_for_status()
        data = response.json()
        ohlcv_list = [
            OHLCV(
                timestamp=item[0],
                open=item[1],
                high=item[2],
                low=item[3],
                close=item[4],
                volume=item[5],
            )
            for item in data["data"]["attributes"]["ohlcv_list"]
        ]
        return GeckoTerminalOHLCVData(ohlcv_list=ohlcv_list)
