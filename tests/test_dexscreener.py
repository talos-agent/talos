from talos.tools.dexscreener import DexscreenerTool
from unittest.mock import patch, MagicMock

@patch('requests.get')
def test_dexscreener_tool(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'<span class="ds-dex-table-row-price">$1.23</span>'
    mock_get.return_value = mock_response
    tool = DexscreenerTool()
    price = tool._run(token_address="0xdaae914e4bae2aae4f536006c353117b90fb37e3")
    assert price.startswith("$")
