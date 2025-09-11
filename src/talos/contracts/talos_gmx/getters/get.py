import logging
from typing import Awaitable, Optional, Literal, overload

from pydantic import BaseModel, Field, PrivateAttr
from eth_typing import HexAddress
from eth_rpc.types.primitives import uint256, int256

from ..constants import DATASTORE_ADDRESS
from ..contracts import synthetics_reader, SyntheticsReader
from ..contracts.synthetics_reader.schemas import GetMarketParams, GetOpenInterestParams, GetPnlParams, PriceProps, MarketProps, MarketUtilsMarketPrices
from ..contracts.synthetics_reader.types import ReaderUtilsMarketInfo
from .markets import Markets
from .prices import OraclePrices
from ..utils.datastore import save_json_file_to_datastore, save_csv_to_datastore, make_timestamped_dataframe


class GetData(BaseModel):
    use_local_datastore: bool = Field(default=False)
    filter_swap_markets: bool = Field(default=True)
    markets: Markets = Field(default_factory=Markets)
    reader_contract: SyntheticsReader = Field(default_factory=lambda: synthetics_reader)

    _long_token_address: Optional[str] = PrivateAttr(default=None)
    _short_token_address: Optional[str] = PrivateAttr(default=None)

    _output: dict[str, dict[str, float]] = PrivateAttr(default_factory=lambda: {
        "long": {},
        "short": {}
    })

    async def load(self) -> None:
        await self.markets.load_info()

    async def get_data(self, to_json: bool = False, to_csv: bool = False):
        if self.filter_swap_markets:
            self._filter_swap_markets()

        data = await self._get_data_processing()

        if to_json:
            parameter = data['parameter']
            save_json_file_to_datastore(
                "{}_data.json".format(parameter),
                data
            )

        if to_csv:
            try:
                parameter = data['parameter']
                dataframe = make_timestamped_dataframe(data['long'])
                save_csv_to_datastore(
                    "long_{}_data.csv".format(parameter),
                    dataframe
                )
                dataframe = make_timestamped_dataframe(data['short'])
                save_csv_to_datastore(
                    "short_{}_data.csv".format(parameter),
                    dataframe
                )
            except KeyError:
                dataframe = make_timestamped_dataframe(data)
                save_csv_to_datastore(
                    "{}_data.csv".format(parameter),
                    dataframe
                )

            except Exception as e:
                logging.info(e)

        return data

    async def _get_data_processing(self):
        pass

    def _get_token_addresses(self, market_key: str):
        self._long_token_address = self.markets.get_long_token_address(
            market_key
        )
        self._short_token_address = self.markets.get_short_token_address(
            market_key
        )
        logging.info(
            "Long Token Address: {}\nShort Token Address: {}".format(
                self._long_token_address, self._short_token_address
            )
        )

    def _filter_swap_markets(self):
        # TODO: Move to markets MAYBE
        keys_to_remove = []
        for market_key in self.markets._info:
            market_symbol = self.markets.get_market_symbol(market_key)
            if 'SWAP' in market_symbol:
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
                maximize=maximize
            )
        ).get()

        pnl = self.reader_contract.get_pnl(
            GetPnlParams(
                data_store=DATASTORE_ADDRESS,
                market=market,
                index_token_price=prices_props,
                is_long=is_long,
                maximize=maximize
            )
        ).get()

        return open_interest_pnl, pnl

    @overload
    async def _get_oracle_prices(
        self,
        market_key: HexAddress,
        index_token_address: str,
        return_tuple: Literal[True],
    ) -> MarketUtilsMarketPrices:
        ...

    @overload
    async def _get_oracle_prices(
        self,
        market_key: HexAddress,
        index_token_address: str,
    ) -> ReaderUtilsMarketInfo:
        ...

    async def _get_oracle_prices(
        self,
        market_key: HexAddress,
        index_token_address: str,
        return_tuple: bool = False
    ) -> ReaderUtilsMarketInfo | MarketUtilsMarketPrices:
        """
        For a given market get the marketInfo from the reader contract

        Parameters
        ----------
        market_key : str
            address of GMX market.
        index_token_address : str
            address of index token.
        long_token_address : str
            address of long collateral token.
        short_token_address : str
            address of short collateral token.

        Returns
        -------
        reader_contract object
            unexecuted reader contract object.

        """
        oracle_prices_dict = await OraclePrices.get_recent_prices()

        try:
            prices = MarketUtilsMarketPrices(
                index_token_price=PriceProps(
                    min=uint256(int(
                        (
                            oracle_prices_dict[index_token_address]
                            ['minPriceFull']
                        )
                    )),
                    max=uint256(int(
                        (
                            oracle_prices_dict[index_token_address]
                            ['maxPriceFull']
                        )
                    ))
                ),
                long_token_price=PriceProps(
                    min=uint256(int(
                        (
                            oracle_prices_dict[self._long_token_address]
                            ['minPriceFull']
                        )
                    )),
                    max=uint256(int(
                        (
                            oracle_prices_dict[self._long_token_address]
                            ['maxPriceFull']
                        )
                    ))
                ),
                short_token_price=PriceProps(
                    min=uint256(int(
                        (
                            oracle_prices_dict[self._short_token_address]
                            ['minPriceFull']
                        )
                    )),
                    max=uint256(int(
                        (
                            oracle_prices_dict[self._short_token_address]
                            ['maxPriceFull']
                        )
                    ))
                ))
        # TODO - this needs to be here until GMX add stables to signed price
        except KeyError:
            prices = MarketUtilsMarketPrices(
                index_token_price=PriceProps(
                    min=uint256(int(
                        oracle_prices_dict[index_token_address]['minPriceFull']
                    )),
                    max=uint256(int(
                        oracle_prices_dict[index_token_address]['maxPriceFull']
                    ))
                ),
                long_token_price=PriceProps(
                    min=uint256(int(
                        (
                            oracle_prices_dict[self._long_token_address]
                            ['minPriceFull']
                        )
                    )),
                    max=uint256(int(
                        (
                            oracle_prices_dict[self._long_token_address]
                            ['maxPriceFull']
                        )
                    ))
                ),
                short_token_price=PriceProps(
                    min=uint256(int(1000000000000000000000000)),
                    max=uint256(int(1000000000000000000000000)),
                )
            )

        if return_tuple:
            return prices

        return await self.reader_contract.get_market_info(
            GetMarketParams(
                data_store=self.data_store_contract_address,
                prices=prices,
                market_key=market_key
            )
        ).get()

    @staticmethod
    def _format_market_info_output(output):
        output = {
            "market_address": output[0][0],
            "index_address": output[0][1],
            "long_address": output[0][2],
            "short_address": output[0][3],

            "borrowingFactorPerSecondForLongs": output[1],
            "borrowingFactorPerSecondForShorts": output[2],

            "baseFunding_long_fundingFeeAmountPerSize_longToken": output[3][0][0][0],
            "baseFundinglong_fundingFeeAmountPerSize_shortToken": output[3][0][0][1],
            "baseFundingshort_fundingFeeAmountPerSize_longToken": output[3][0][1][0],
            "baseFundingshort_fundingFeeAmountPerSize_shortToken": output[3][0][1][1],
            "baseFundinglong_claimableFundingAmountPerSize_longToken": output[3][1][0][0],
            "baseFundinglong_claimableFundingAmountPerSize_shortToken": output[3][1][0][1],
            "baseFundingshort_claimableFundingAmountPerSize_longToken": output[3][1][1][0],
            "baseFundingshort_claimableFundingAmountPerSize_shortToken": output[3][1][1][1],

            "longsPayShorts": output[4][0],
            "fundingFactorPerSecond": output[4][1],
            "nextSavedFundingFactorPerSecond": output[4][2],

            "nextFunding_long_fundingFeeAmountPerSize_longToken": output[4][3][0][0],
            "nextFunding_long_fundingFeeAmountPerSize_shortToken": output[4][3][0][1],
            "nextFunding_baseFundingshort_fundingFeeAmountPerSize_longToken": output[4][3][1][0],
            "nextFunding_baseFundingshort_fundingFeeAmountPerSize_shortToken": output[4][3][1][1],
            "nextFunding_baseFundinglong_claimableFundingAmountPerSize_longToken": output[4][4][0][0],
            "nextFunding_baseFundinglong_claimableFundingAmountPerSize_shortToken": output[4][4][0][1],
            "nextFunding_baseFundingshort_claimableFundingAmountPerSize_longToken": output[4][4][1][0],
            "nextFunding_baseFundingshort_claimableFundingAmountPerSize_shortToken": output[4][4][1][1],

            "virtualPoolAmountForLongToken": output[5][0],
            "virtualPoolAmountForShortToken": output[5][1],
            "virtualInventoryForPositions": output[5][2],

            "isDisabled": output[6],
        }
        return output

    @property
    def output(self):
        return self._output
