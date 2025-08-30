
from talos.models.gecko_terminal import OHLCV, GeckoTerminalOHLCVData
from talos.utils.http_client import SecureHTTPClient


class GeckoTerminalClient:
    def __init__(self, network: str = "arbitrum", pool_address: str = "0xdaAe914e4Bae2AAe4f536006C353117B90Fb37e3"):
        from talos.utils.validation import sanitize_user_input
        self.network = sanitize_user_input(network, max_length=50)
        self.pool_address = sanitize_user_input(pool_address, max_length=100)

    def get_ohlcv_data(self, timeframe: str = "hour") -> GeckoTerminalOHLCVData:
        """Gets the OHLCV data for a token from geckoterminal.com"""
        from talos.utils.validation import sanitize_user_input
        timeframe = sanitize_user_input(timeframe, max_length=20)
        
        url = (
            f"https://api.geckoterminal.com/api/v2/networks/{self.network}/pools/{self.pool_address}/ohlcv/{timeframe}"
        )
        http_client = SecureHTTPClient()
        response = http_client.get(url, headers={"accept": "application/json"})
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
