from talos.tools.dexscreener import DexscreenerTool
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_dexscreener_tool(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'<span class="ds-dex-table-row-price">$1.23</span><div class="Percentage-sc-1xf18x6-0">1.59%</div><div class="Block-sc-1xf18x6-0">$1.0M</div>'
    mock_get.return_value = mock_response
    tool = DexscreenerTool()
    price_data = tool._run(token_address="0xdaae914e4bae2aae4f536006c353117b90fb37e3")
    assert price_data["price"].startswith("$")
    assert price_data["change"].endswith("%")
    assert price_data["volume"].startswith("$")
