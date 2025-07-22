from unittest.mock import MagicMock, patch

from talos.tools.dexscreener import DexscreenerTool


@patch("requests.get")
def test_dexscreener_tool(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"pair": {"priceUsd": "1.23", "priceChange": 1.59, "volume": 1000000}}
    mock_get.return_value = mock_response
    tool = DexscreenerTool()
    price_data = tool._run(token_address="0xdaae914e4bae2aae4f536006c353117b90fb37e3")
    assert price_data.price_usd == 1.23
    assert price_data.price_change_h24 == 1.59
    assert price_data.volume_h24 == 1000000
