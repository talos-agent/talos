import requests
from bs4 import BeautifulSoup
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class DexscreenerToolArgs(BaseModel):
    token_address: str = Field(..., description="The address of the token to get the price for")

class DexscreenerTool(BaseTool):
    name: str = "dexscreener_tool"
    description: str = "Gets the price of a token from dexscreener.com"
    args_schema: type[BaseModel] = DexscreenerToolArgs

    def _run(self, token_address: str) -> str:
        """Gets the price of a token from dexscreener.com"""
        url = f"https://dexscreener.com/arbitrum/{token_address}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"
        soup = BeautifulSoup(response.content, "html.parser")
        price_element = soup.find("span", class_="ds-dex-table-row-price")
        if price_element:
            return price_element.text
        else:
            return "Error: Could not find price information"
