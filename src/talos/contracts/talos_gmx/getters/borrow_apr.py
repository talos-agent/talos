import asyncio
import logging

from ..contracts.synthetics_reader.types import ReaderUtilsMarketInfo
from .get import GetData


class GetBorrowAPR(GetData):
    async def _get_data_processing(self) -> dict[str, dict[str, str | float] | str]:
        """
        Generate the dictionary of borrow APR data

        Returns
        -------
        funding_apr : dict
            dictionary of borrow data.

        """
        output_list = []
        mapper = []
        for market_key in self.markets._info:
            index_token_address = self.markets.get_index_token_address(market_key)

            self._get_token_addresses(market_key)
            output = self._get_oracle_prices(
                market_key,
                index_token_address,
            )

            output_list.append(output)
            mapper.append(self.markets.get_market_symbol(market_key))

        threaded_output: list[ReaderUtilsMarketInfo] = await asyncio.gather(*output_list)

        for key, market_info in zip(mapper, threaded_output):
            self._output["long"][key] = (market_info.borrowing_factor_per_second_for_longs / 10**28) * 3600  # type: ignore
            self._output["short"][key] = (market_info.borrowing_factor_per_second_for_shorts / 10**28) * 3600  # type: ignore

            logging.info(
                ("{}\nLong Borrow Hourly Rate: -{:.5f}%\nShort Borrow Hourly Rate: -{:.5f}%\n").format(
                    key,
                    self._output["long"][key],  # type: ignore
                    self._output["short"][key],  # type: ignore
                )
            )

        self._output["parameter"] = "borrow_apr"

        return self._output
