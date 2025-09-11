import logging
import numpy as np

from eth_rpc.utils import to_checksum
from eth_typing import HexAddress

from ..contracts import synthetics_reader
from ..constants import DATASTORE_ADDRESS
from ..contracts.synthetics_reader import PositionProps
from ..types import Position
from .get import GetData
from .prices import OraclePrices

from ..utils import get_tokens_address_dict

chain = 'arbitrum'


class GetOpenPositions(GetData):
    address: HexAddress

    def __init__(self, address: HexAddress, **kwargs):
        super().__init__(address=to_checksum(address), **kwargs)

    async def get_data(self) -> dict[str, Position]:
        """
        Get all open positions for a given address on the chain defined in
        class init

        Parameters
        ----------
        address : str
            evm address .

        Returns
        -------
        processed_positions : dict
            a dictionary containing the open positions, where asset and
            direction are the keys.

        """
        raw_positions = await synthetics_reader.get_account_positions(
            DATASTORE_ADDRESS,
            self.address,
            0,
            10
        ).get()

        if len(raw_positions) == 0:
            logging.info(
                'No positions open for address: "{}"'.format(
                    self.address,
                )
            )
        processed_positions = {}

        for raw_position in raw_positions:
            try:
                processed_position = await self._get_data_processing(raw_position)

                # TODO - maybe a better way of building the key?
                if processed_position.is_long:
                    direction = 'long'
                else:
                    direction = 'short'

                key = "{}_{}".format(
                    processed_position.market_symbol,
                    direction
                )
                processed_positions[key] = processed_position
            except KeyError as e:
                logging.error(f"Incompatible market: {e}")

        return processed_positions

    async def _get_data_processing(self, raw_position: PositionProps) -> Position:
        """
        A tuple containing the raw information return from the reader contract
        query GetAccountPositions

        Parameters
        ----------
        raw_position : tuple
            raw information return from the reader contract .

        Returns
        -------
        dict
            a processed dictionary containing info on the positions.
        """
        market_info = self.markets.info[raw_position.addresses.market]

        chain_tokens = await get_tokens_address_dict()

        entry_price = (
            raw_position.numbers.size_in_usd / raw_position.numbers.size_in_tokens
        ) / 10 ** (
            30 - chain_tokens[market_info['index_token_address']]['decimals']
        )

        leverage = (
            raw_position.numbers.size_in_usd / 10 ** 30
        ) / (
            raw_position.numbers.collateral_amount / 10 ** chain_tokens[
                raw_position.addresses.collateral_token
            ]['decimals']
        )
        prices = await OraclePrices().get_recent_prices()
        mark_price = np.median(
            [
                float(
                    prices[market_info['index_token_address']]['maxPriceFull']
                ),
                float(
                    prices[market_info['index_token_address']]['minPriceFull']
                )
            ]
        ) / 10 ** (
            30 - chain_tokens[market_info['index_token_address']]['decimals']
        )

        return Position(
            account=raw_position.addresses.account,
            market=raw_position.addresses.market,
            market_symbol=self.markets.info[raw_position.addresses.market]['market_symbol'],
            collateral_token=chain_tokens[raw_position.addresses.collateral_token]['symbol'],
            position_size=raw_position.numbers.size_in_usd / 10**30,
            size_in_tokens=raw_position.numbers.size_in_tokens,
            entry_price=(
                (
                    raw_position.numbers.size_in_usd / raw_position.numbers.size_in_tokens
                ) / 10 ** (
                    30 - chain_tokens[
                        market_info['index_token_address']
                    ]['decimals']
                )
            ),
            inital_collateral_amount=raw_position.numbers.collateral_amount,
            inital_collateral_amount_usd=(
                raw_position.numbers.collateral_amount
                / 10 ** chain_tokens[raw_position.addresses.collateral_token]['decimals']
            ),
            leverage=leverage,
            borrowing_factor=raw_position.numbers.borrowing_factor,
            funding_fee_amount_per_size=raw_position.numbers.funding_fee_amount_per_size,
            long_token_claimable_funding_amount_per_size=raw_position.numbers.long_token_claimable_funding_amount_per_size,
            short_token_claimable_funding_amount_per_size=raw_position.numbers.short_token_claimable_funding_amount_per_size,
            position_modified_at="",
            is_long=raw_position.flags.is_long,
            percent_profit=(
                (
                    1 - (mark_price / entry_price)
                ) * leverage
            ) * 100,
            mark_price=mark_price,
        )
