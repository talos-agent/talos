import asyncio
import logging

from eth_rpc.types.primitives import uint256
from eth_rpc.utils import to_checksum
from eth_typing import ChecksumAddress
from pydantic import BaseModel, PrivateAttr

from ..constants import DATASTORE_ADDRESS
from ..contracts import synthetics_reader
from ..contracts.synthetics_reader import GetMarketsParams, MarketProps
from ..types.markets import Market, MarketMetadata
from ..utils.tokens import get_tokens_address_dict
from .prices import OraclePrices


class Markets(BaseModel):
    _info: dict[ChecksumAddress, Market] = PrivateAttr(default_factory=dict)

    async def load_info(self) -> dict[ChecksumAddress, Market]:
        if not self._info:
            self._info = await self._process_markets()
        return self._info

    def get_index_token_address(self, market_key: ChecksumAddress) -> ChecksumAddress:
        return self._info[market_key].index_token_address

    def get_long_token_address(self, market_key: ChecksumAddress) -> ChecksumAddress:
        return self._info[market_key].long_token_address

    def get_short_token_address(self, market_key: ChecksumAddress) -> ChecksumAddress:
        return self._info[market_key].short_token_address

    def get_market_symbol(self, market_key: ChecksumAddress) -> str:
        return self._info[market_key].market_symbol

    def get_decimal_factor(self, market_key: ChecksumAddress, long: bool = False, short: bool = False) -> int:
        if long:
            return self._info[market_key].long_token_metadata.decimals
        elif short:
            return self._info[market_key].short_token_metadata.decimals
        else:
            return self._info[market_key].market_metadata.decimals

    def is_synthetic(self, market_key: ChecksumAddress) -> bool:
        return self._info[market_key].market_metadata.synthetic

    async def get_available_markets(self) -> dict[ChecksumAddress, Market]:
        """
        Get the available markets on a given chain

        Returns
        -------
        Markets: dict
            dictionary of the available markets.

        """
        logging.info("Getting Available Markets..")
        return await self._process_markets()

    async def _get_available_markets_raw(self) -> list[MarketProps]:
        """
        Get the available markets from the reader contract

        Returns
        -------
        Markets: tuple
            tuple of raw output from the reader contract.

        """

        response = await synthetics_reader.get_markets(
            GetMarketsParams(
                data_store=DATASTORE_ADDRESS,
                start_index=uint256(0),
                end_index=uint256(50),
            )
        ).get()

        return response  # type: ignore

    async def _process_markets(self) -> dict[ChecksumAddress, Market]:
        """
        Call and process the raw market data

        Returns
        -------
        decoded_markets : dict
            dictionary decoded market data.

        """
        decoded_markets = {}

        token_address_dict, raw_markets = await asyncio.gather(
            get_tokens_address_dict(), self._get_available_markets_raw()
        )
        checks = await asyncio.gather(
            *[
                self._check_if_index_token_in_signed_prices_api(to_checksum(raw_market.index_token))
                for raw_market in raw_markets
            ]
        )

        for raw_market, check in zip(raw_markets, checks):
            if not check:
                continue
            try:
                market_symbol = token_address_dict[to_checksum(raw_market.index_token)].symbol

                if raw_market.long_token == raw_market.short_token:
                    market_symbol = f"{market_symbol}2"
                decoded_markets[to_checksum(raw_market.market_token)] = Market(
                    address=to_checksum(raw_market.market_token),
                    market_symbol=market_symbol,
                    index_token_address=to_checksum(raw_market.index_token),
                    market_metadata=token_address_dict[to_checksum(raw_market.index_token)],
                    long_token_metadata=token_address_dict[to_checksum(raw_market.long_token)],
                    long_token_address=to_checksum(raw_market.long_token),
                    short_token_metadata=token_address_dict[to_checksum(raw_market.short_token)],
                    short_token_address=to_checksum(raw_market.short_token),
                )
                if raw_market.market_token == "0x0Cf1fb4d1FF67A3D8Ca92c9d6643F8F9be8e03E5":
                    decoded_markets[to_checksum(raw_market.market_token)].market_symbol = "wstETH"
                    decoded_markets[to_checksum(raw_market.market_token)].index_token_address = to_checksum(
                        "0x5979D7b546E38E414F7E9822514be443A4800529"
                    )

            # If KeyError it is because there is no market symbol and it is a
            # swap market
            except KeyError:
                decoded_markets[to_checksum(raw_market.market_token)] = Market(
                    address=to_checksum(raw_market.market_token),
                    market_symbol="SWAP {}-{}".format(
                        token_address_dict[to_checksum(raw_market.long_token)].symbol,
                        token_address_dict[to_checksum(raw_market.short_token)].symbol,
                    ),
                    index_token_address=to_checksum(raw_market.index_token),
                    market_metadata=MarketMetadata(
                        symbol="SWAP {}-{}".format(
                            token_address_dict[to_checksum(raw_market.long_token)].symbol,
                            token_address_dict[to_checksum(raw_market.short_token)].symbol,
                        )
                    ),
                    long_token_metadata=token_address_dict[to_checksum(raw_market.long_token)],
                    long_token_address=to_checksum(raw_market.long_token),
                    short_token_metadata=token_address_dict[to_checksum(raw_market.short_token)],
                    short_token_address=to_checksum(raw_market.short_token),
                )

        return decoded_markets

    async def _check_if_index_token_in_signed_prices_api(self, index_token_address: ChecksumAddress) -> bool:
        try:
            prices = await OraclePrices.get_recent_prices()

            if index_token_address == "0x0000000000000000000000000000000000000000":
                return True
            prices[to_checksum(index_token_address)]
            return True
        except KeyError:
            print("{} market not live on GMX yet..".format(index_token_address))
            return False

    @property
    def info(self) -> dict[ChecksumAddress, Market]:
        return self._info
