import asyncio
import logging
from numerize import numerize
from typing import Awaitable

from eth_rpc.types.primitives import int256

from .get import GetData
from .prices import OraclePrices
from ..contracts.synthetics_reader.schemas import MarketProps, PriceProps

class OpenInterest(GetData):
    async def _get_data_processing(self):
        """
        Generate the dictionary of open interest data

        Returns
        -------
        funding_apr : dict
            dictionary of open interest data.

        """
        oracle_prices_dict = await OraclePrices.get_recent_prices()
        print("GMX v2 Open Interest\n")

        long_oi_output_list: list[Awaitable[int256]] = []
        short_oi_output_list: list[Awaitable[int256]] = []
        long_pnl_output_list: list[Awaitable[int256]] = []
        short_pnl_output_list: list[Awaitable[int256]] = []
        mapper = []
        long_precision_list = []

        for market_key in self.markets.info:
            self._filter_swap_markets()
            self._get_token_addresses(market_key)

            index_token_address = self.markets.get_index_token_address(
                market_key
            )

            market = MarketProps(
                market_token=market_key,
                index_token=index_token_address,
                long_token=self._long_token_address,
                short_token=self._short_token_address
            )

            min_price = int(
                oracle_prices_dict[index_token_address]['minPriceFull']
            )
            max_price = int(
                oracle_prices_dict[index_token_address]['maxPriceFull']
            )
            price_props = PriceProps(min=min_price, max=max_price)

            # If the market is a synthetic one we need to use the decimals
            # from the index token
            try:
                if self.markets.is_synthetic(market_key):
                    decimal_factor = self.markets.get_decimal_factor(
                        market_key,
                    )
                else:
                    decimal_factor = self.markets.get_decimal_factor(
                        market_key,
                        long=True
                    )
            except KeyError:
                decimal_factor = self.markets.get_decimal_factor(
                    market_key,
                    long=True
                )

            oracle_factor = (30 - decimal_factor)
            precision = 10 ** (decimal_factor + oracle_factor)
            long_precision_list = long_precision_list + [precision]

            long_oi_with_pnl, long_pnl = self._get_pnl(
                market,
                price_props,
                is_long=True
            )

            short_oi_with_pnl, short_pnl = self._get_pnl(
                market,
                price_props,
                is_long=False
            )

            long_oi_output_list.append(long_oi_with_pnl)
            short_oi_output_list.append(short_oi_with_pnl)
            long_pnl_output_list.append(long_pnl)
            short_pnl_output_list.append(short_pnl)
            mapper.append(self.markets.get_market_symbol(market_key))

        # TODO - currently just waiting x amount of time to not hit rate limit,
        # but needs a retry
        long_oi_threaded_output = await asyncio.gather(*long_oi_output_list)
        await asyncio.sleep(2)
        short_oi_threaded_output = await asyncio.gather(*short_oi_output_list)
        await asyncio.sleep(2)
        long_pnl_threaded_output = await asyncio.gather(*long_pnl_output_list)
        await asyncio.sleep(2)
        short_pnl_threaded_output = await asyncio.gather(*short_pnl_output_list)

        for (
            market_symbol,
            long_oi,
            short_oi,
            long_pnl,
            short_pnl,
            long_precision
        ) in zip(
            mapper,
            long_oi_threaded_output,
            short_oi_threaded_output,
            long_pnl_threaded_output,
            short_pnl_threaded_output,
            long_precision_list
        ):
            precision = 10 ** 30
            long_value = (long_oi - long_pnl) / long_precision
            short_value = (short_oi - short_pnl) / precision

            logging.info(
                f"{market_symbol} Long: ${numerize.numerize(long_value)}"
            )
            logging.info(
                f"{market_symbol} Short: ${numerize.numerize(short_value)}"
            )

            self.output['long'][market_symbol] = long_value
            self.output['short'][market_symbol] = short_value
        self.output['parameter'] = "open_interest"

        return self.output


if __name__ == '__main__':
    data = OpenInterest().get_data(to_csv=False)
    print(data)
