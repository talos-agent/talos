from __future__ import annotations

from typing import Any
import requests

from pydantic import BaseModel


class PerplexityService(BaseModel):
    """
    A service for fetching data from the Perplexity API.
    """

    base_url: str = "https://api.perplexity.ai"
    token: str

    def search(self, query: str) -> dict[str, Any]:
        """
        Submits a query to the Perplexity API and returns the response.
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        data = {"query": query}
        response = requests.post(f"{self.base_url}/search", headers=headers, json=data)
        response.raise_for_status()
        return response.json()