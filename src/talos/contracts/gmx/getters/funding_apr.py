import asyncio
import json
import os
from typing import Awaitable

from pydantic import Field

from ..contracts.synthetics_reader.types import ReaderUtilsMarketInfo
from ..utils.funding import get_funding_factor_per_period
from .get import GetData
from .open_interest import OpenInterest

base_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data_store")


class GetFundingFee(GetData):
    open_interest: OpenInterest = Field(default_factory=OpenInterest)

    async def _get_data_processing(self) -> dict[str, dict[str, str | float] | str]:
        """
        Generate the dictionary of funding APR data

        Returns
        -------
        funding_apr : dict
            dictionary of funding data.

        """

        # If passing true will use local instance of open interest data
        if self.use_local_datastore:
            open_interest = json.load(open(os.path.join(base_dir, "data_store", "open_interest.json")))
        else:
            open_interest = await self.open_interest.get_data(to_json=False)

        print("\nGMX v2 Funding Rates (% per hour)")

        # define empty lists to pass to zip iterater later on
        mapper = []
        output_list: list[Awaitable[ReaderUtilsMarketInfo]] = []
        long_interest_usd_list: list[int] = []
        short_interest_usd_list: list[int] = []

        # loop markets
        for market_key in self.markets._info:
            symbol = self.markets.get_market_symbol(market_key)
            index_token_address = self.markets.get_index_token_address(market_key)
            self._get_token_addresses(market_key)

            output: Awaitable[ReaderUtilsMarketInfo] = self._get_oracle_prices(
                market_key,
                index_token_address,
            )

            mapper.append(symbol)
            output_list.append(output)
            long_interest_usd_list = long_interest_usd_list + [open_interest["long"][symbol] * 10**30]
            short_interest_usd_list = short_interest_usd_list + [open_interest["short"][symbol] * 10**30]

        # Multithreaded call on contract
        threaded_output: list[ReaderUtilsMarketInfo] = await asyncio.gather(*output_list)

        for market_info, long_interest_usd, short_interest_usd, symbol in zip(
            threaded_output, long_interest_usd_list, short_interest_usd_list, mapper
        ):
            print("\n{}".format(symbol))

            long_funding_fee = get_funding_factor_per_period(
                market_info, True, 3600, long_interest_usd, short_interest_usd
            )
            print("Long funding hrly rate {:.4f}%".format(long_funding_fee))

            short_funding_fee = get_funding_factor_per_period(
                market_info, False, 3600, long_interest_usd, short_interest_usd
            )
            print("Short funding hrly rate {:.4f}%".format(short_funding_fee))

            self.output["long"][symbol] = long_funding_fee  # type: ignore
            self.output["short"][symbol] = short_funding_fee  # type: ignore

        self.output["parameter"] = "funding_apr"

        return self.output
