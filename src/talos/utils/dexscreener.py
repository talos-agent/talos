import requests


def get_ohlcv_data(pair_address: str) -> dict:
    """Gets the OHLCV data for a token from dexscreener.com"""
    url = f"https://api.dexscreener.com/latest/dex/pairs/arbitrum/{pair_address}"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": f"Received status code {response.status_code}"}
    data = response.json()
    return data.get("pair", {})
