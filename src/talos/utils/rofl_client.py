import json
import logging
from typing import Any

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class RoflClient:
    """Utility for interacting with ROFL runtime services.

    Provides methods for key fetching and transaction submission
    through the ROFL application daemon.
    """

    ROFL_SOCKET_PATH: str = "/run/rofl-appd.sock"

    def __init__(self, url: str = "") -> None:
        """Initialize ROFL utility.

        Args:
            url: Optional URL for HTTP transport (defaults to socket)
        """
        self.url: str = url

    async def _appd_post(self, path: str, payload: Any) -> Any:
        """Post request to ROFL application daemon.

        Args:
            path: API endpoint path
            payload: JSON payload to send

        Returns:
            JSON response from the daemon

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        transport: httpx.AsyncHTTPTransport | None = None

        if self.url and not self.url.startswith("http"):
            transport = httpx.AsyncHTTPTransport(uds=self.url)
            logger.debug(f"Using HTTP socket: {self.url}")
        elif not self.url:
            transport = httpx.AsyncHTTPTransport(uds=self.ROFL_SOCKET_PATH)
            logger.debug(f"Using unix domain socket: {self.ROFL_SOCKET_PATH}")

        async with httpx.AsyncClient(transport=transport) as client:
            base_url: str = self.url if self.url and self.url.startswith("http") else "http://localhost"
            full_url: str = base_url + path
            logger.debug(f"Posting to {full_url}: {json.dumps(payload)}")
            response: httpx.Response = await client.post(full_url, json=payload, timeout=60.0)
            response.raise_for_status()
            return response.json()

    async def generate_key(self, key_id: str) -> str:
        """Fetch or generate a cryptographic key from ROFL.

        Args:
            key_id: Identifier for the key

        Returns:
            The private key as a hex string

        Raises:
            httpx.HTTPStatusError: If key fetch fails
        """
        payload: dict[str, str] = {"key_id": key_id, "kind": "secp256k1"}

        path: str = "/rofl/v1/keys/generate"
        response: dict[str, Any] = await self._appd_post(path, payload)
        return response["key"]
