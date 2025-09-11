import logging
from typing import Any, Awaitable, Literal, Optional, overload

from eth_rpc.types.primitives import int256, uint256
from eth_typing import ChecksumAddress
from pydantic import BaseModel, Field, PrivateAttr

from ..constants import DATASTORE_ADDRESS
from ..contracts import SyntheticsReader, synthetics_reader
from ..contracts.synthetics_reader import (
    GetMarketParams,
    GetOpenInterestParams,
    GetPnlParams,
    MarketProps,
    MarketUtilsMarketPrices,
    PriceProps,
)
from ..contracts.synthetics_reader.types import ReaderUtilsMarketInfo
from ..utils.datastore import make_timestamped_dataframe, save_csv_to_datastore, save_json_file_to_datastore
from .markets import Markets
from .prices import OraclePrices


class GetData(BaseModel):
    use_local_datastore: bool = Field(default=False)
    filter_swap_markets: bool = Field(default=True)
    markets: Markets = Field(default_factory=Markets)
    reader_contract: SyntheticsReader = Field(default_factory=lambda: synthetics_reader)

    _long_token_address: Optional[ChecksumAddress] = PrivateAttr(default=None)
    _short_token_address: Optional[ChecksumAddress] = PrivateAttr(default=None)

    _output: dict[str, dict[str, str | float] | str] = PrivateAttr(default_factory=lambda: {"long": {}, "short": {}})

    async def load(self) -> None:
        await self.markets.load_info()

    async def get_data(self, to_json: bool = False, to_csv: bool = False) -> dict[str, Any]:
        if self.filter_swap_markets:
            self._filter_swap_markets()

        data = await self._get_data_processing()

        if to_json:
            parameter = data["parameter"]
            save_json_file_to_datastore("{}_data.json".format(parameter), data)

        if to_csv:
            try:
                parameter = data["parameter"]
                dataframe = make_timestamped_dataframe(data["long"])
                save_csv_to_datastore("long_{}_data.csv".format(parameter), dataframe)
                dataframe = make_timestamped_dataframe(data["short"])
                save_csv_to_datastore("short_{}_data.csv".format(parameter), dataframe)
            except KeyError:
                dataframe = make_timestamped_dataframe(data)
                save_csv_to_datastore("{}_data.csv".format(parameter), dataframe)

            except Exception as e:
                logging.info(e)

        return data

    async def _get_data_processing(self) -> dict[str, Any]:
        raise NotImplementedError()

    def _get_token_addresses(self, market_key: ChecksumAddress) -> None:
        self._long_token_address = self.markets.get_long_token_address(market_key)
        self._short_token_address = self.markets.get_short_token_address(market_key)
        logging.info(
            "Long Token Address: {}\nShort Token Address: {}".format(
                self._long_token_address, self._short_token_address
            )
        )

    def _filter_swap_markets(self) -> None:
        # TODO: Move to markets MAYBE
        keys_to_remove = []
        for market_key in self.markets._info:
            market_symbol = self.markets.get_market_symbol(market_key)
            if "SWAP" in market_symbol:
                # Remove swap markets from dict
                keys_to_remove.append(market_key)

        [self.markets._info.pop(k) for k in keys_to_remove]

    def _get_pnl(
        self,
        market: MarketProps,
        prices_props: PriceProps,
        is_long: bool,
        maximize: bool = False,
    ) -> tuple[Awaitable[int256], Awaitable[int256]]:
        """returns two coroutines"""
        open_interest_pnl = self.reader_contract.get_open_interest_with_pnl(
            GetOpenInterestParams(
                data_store=DATASTORE_ADDRESS,
                market=market,
                index_token_price=prices_props,
                is_long=is_long,
                maximize=maximize,
            )
        ).get()

        pnl = self.reader_contract.get_pnl(
            GetPnlParams(
                data_store=DATASTORE_ADDRESS,
                market=market,
                index_token_price=prices_props,
                is_long=is_long,
                maximize=maximize,
            )
        ).get()

        return open_interest_pnl, pnl

    @overload
    async def _get_oracle_prices(
        self,
        market_key: ChecksumAddress,
        index_token_address: ChecksumAddress,
        return_tuple: Literal[True],
    ) -> MarketUtilsMarketPrices: ...

    @overload
    async def _get_oracle_prices(
        self,
        market_key: ChecksumAddress,
        index_token_address: ChecksumAddress,
    ) -> ReaderUtilsMarketInfo: ...

    async def _get_oracle_prices(
        self,
        market_key: ChecksumAddress,
        index_token_address: ChecksumAddress,
        return_tuple: bool = False,
    ) -> ReaderUtilsMarketInfo | MarketUtilsMarketPrices:
        """
        For a given market get the marketInfo from the reader contract
        """

        oracle_prices_dict = await OraclePrices.get_recent_prices()

        assert self._long_token_address is not None
        assert self._short_token_address is not None

        try:
            prices = MarketUtilsMarketPrices(
                index_token_price=PriceProps(
                    min=uint256(int((oracle_prices_dict[index_token_address].min_price_full))),
                    max=uint256(int((oracle_prices_dict[index_token_address].max_price_full))),
                ),
                long_token_price=PriceProps(
                    min=uint256(int(oracle_prices_dict[self._long_token_address].min_price_full)),
                    max=uint256(int(oracle_prices_dict[self._long_token_address].max_price_full)),
                ),
                short_token_price=PriceProps(
                    min=uint256(int(oracle_prices_dict[self._short_token_address].min_price_full)),
                    max=uint256(int(oracle_prices_dict[self._short_token_address].max_price_full)),
                ),
            )
        # TODO - this needs to be here until GMX add stables to signed price
        except KeyError:
            prices = MarketUtilsMarketPrices(
                index_token_price=PriceProps(
                    min=uint256(int(oracle_prices_dict[index_token_address].min_price_full)),
                    max=uint256(int(oracle_prices_dict[index_token_address].max_price_full)),
                ),
                long_token_price=PriceProps(
                    min=uint256(int(oracle_prices_dict[self._long_token_address].min_price_full)),
                    max=uint256(int(oracle_prices_dict[self._long_token_address].max_price_full)),
                ),
                short_token_price=PriceProps(
                    min=uint256(int(1000000000000000000000000)),
                    max=uint256(int(1000000000000000000000000)),
                ),
            )

        if return_tuple:
            return prices

        response: ReaderUtilsMarketInfo = await self.reader_contract.get_market_info(
            GetMarketParams(
                data_store=DATASTORE_ADDRESS,
                prices=prices,
                market_key=market_key,
            )
        ).get()
        return response

    @property
    def output(self) -> dict[str, dict[str, str | float] | str]:
        return self._output
