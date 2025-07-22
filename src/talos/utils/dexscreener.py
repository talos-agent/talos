import requests

from talos.models.dexscreener import DexscreenerData


class DexscreenerClient:
    def __init__(self, pair_address: str = "0xdaae914e4bae2aae4f536006c353117b90fb37e3"):
        # $T pair address on arbitrum
        self.pair_address = pair_address
        
        # ARB pair address on arbitrum
        self.arb_pair_address = "0xC6F780497A95e246EB9449f5e4770916DCd6396A"

    def get_talos_data(self) -> DexscreenerData:
        """Gets the OHLCV data for a token from dexscreener.com"""
        url = f"https://api.dexscreener.com/latest/dex/pairs/arbitrum/{self.pair_address}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Handle the nested data structure
        pair_data = data.get("pair", {})
        
        # Extract 24h values from the nested structure
        price_change_24h = pair_data.get("priceChange", {}).get("h24", 0.0)
        volume_24h = pair_data.get("volume", {}).get("h24", 0.0)
        
        # Create a modified data structure that matches DexscreenerData
        talos_data = {
            "priceUsd": pair_data.get("priceUsd", 0.0),
            "priceChange": price_change_24h,
            "volume": volume_24h
        }
        
        return DexscreenerData.model_validate(talos_data)
    
    def get_arb_data(self) -> DexscreenerData:
        """Gets ETH price data from dexscreener.com"""
        url = f"https://api.dexscreener.com/latest/dex/pairs/arbitrum/{self.arb_pair_address}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Handle the different data structure for ARB pair
        pair_data = data.get("pair", {})
        
        # Extract 24h values from the nested structure
        price_change_24h = pair_data.get("priceChange", {}).get("h24", 0.0)
        volume_24h = pair_data.get("volume", {}).get("h24", 0.0)
        
        # Create a modified data structure that matches DexscreenerData
        arb_data = {
            "priceUsd": pair_data.get("priceUsd", 0.0),
            "priceChange": price_change_24h,
            "volume": volume_24h
        }
        
        return DexscreenerData.model_validate(arb_data)


def get_ohlcv_data(pair_address: str) -> DexscreenerData:
    """Gets the OHLCV data for a token from dexscreener.com"""
    client = DexscreenerClient(pair_address)
    return client.get_talos_data()
