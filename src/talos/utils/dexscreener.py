
from talos.models.dexscreener import DexscreenerData
from talos.utils.http_client import SecureHTTPClient


class DexscreenerClient:
    def __init__(self, pair_address: str = "0xdaae914e4bae2aae4f536006c353117b90fb37e3"):
        from talos.utils.validation import sanitize_user_input
        self.pair_address = sanitize_user_input(pair_address, max_length=100)

    def get_talos_data(self) -> DexscreenerData:
        """Gets the OHLCV data for a token from dexscreener.com"""
        url = f"https://api.dexscreener.com/latest/dex/pairs/arbitrum/{self.pair_address}"
        http_client = SecureHTTPClient()
        response = http_client.get(url)
        data = response.json()
        return DexscreenerData.model_validate(data.get("pair", {}))


def get_ohlcv_data(pair_address: str) -> DexscreenerData:
    """Gets the OHLCV data for a token from dexscreener.com"""
    client = DexscreenerClient(pair_address)
    return client.get_talos_data()
