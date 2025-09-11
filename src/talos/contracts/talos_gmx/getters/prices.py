from typing import ClassVar

import httpx

from pydantic import BaseModel


class OraclePrices(BaseModel):
    ORACLE_URL: ClassVar[str] = "https://arbitrum-api.gmxinfra.io/signed_prices/latest"

    @classmethod
    async def get_recent_prices(cls) -> dict:
        """
        Get raw output of the GMX rest v2 api for signed prices

        Returns
        -------
        dict
            dictionary containing raw output for each token as its keys.

        """
        raw_output = await cls._make_query()
        return cls._process_output(raw_output)

    @classmethod
    async def _make_query(cls) -> dict:
        """
        Make request using oracle url

        Returns
        -------
        requests.models.Response
            raw request response.

        """
        async with httpx.AsyncClient() as client:
            response = await client.get(cls.ORACLE_URL)
        return response.json()

    @classmethod
    def _process_output(cls, output: dict) -> dict:  # noqa: ANN102
        """
        Take the API response and create a new dictionary where the index token
        addresses are the keys

        Parameters
        ----------
        output : dict
            Dictionary of rest API repsonse.

        Returns
        -------
        processed : TYPE
            DESCRIPTION.

        """
        processed = {}
        for i in output['signedPrices']:
            processed[i['tokenAddress']] = i

        return processed
