import asyncio
import logging

from eth_typing import HexAddress, HexStr
from eth_rpc import PrivateKeyWallet

from ..contracts import datastore, exchange_router
from .get import GetData
from .prices import OraclePrices
from ..utils import median, numerize
from ..utils.keys import claimable_fee_amount_key, claimable_funding_amount_key


class GetClaimableFees(GetData):
    """
    Get total fees dictionary

    > await GetClaimableFees().get_data()
    """

    async def claim_market_fees(self, market: HexAddress, token: HexAddress, wallet: PrivateKeyWallet) -> HexStr | None:
        claimable_fee = await self.get_claimable_funding_fees(market, token, wallet.address)
        if claimable_fee > 0:
            tx_hash = await exchange_router.claim_funding_fees(market, token, wallet.address).execute(wallet)
            return tx_hash
        return None

    async def get_claimable_funding_fees(self, market: HexAddress, token: HexAddress, address: HexAddress):
        claimable_fee = claimable_funding_amount_key(market, token, address)
        claimable_fee = await datastore.get_uint(claimable_fee).get()
        return claimable_fee

    async def _get_data_processing(self):
        """
        Get total fees dictionary

        Returns
        -------
        funding_apr : dict
            dictionary of total fees for week so far.

        """
        total_fees = 0
        long_output_list = []
        short_output_list = []
        long_precision_list = []
        long_token_price_list = []
        mapper = []

        for market_key in self.markets.info:
            self._filter_swap_markets()
            self._get_token_addresses(market_key)
            market_symbol = self.markets.get_market_symbol(market_key)
            long_decimal_factor = self.markets.get_decimal_factor(
                market_key=market_key,
                long=True,
                short=False
            )
            long_precision = 10**(long_decimal_factor - 1)
            oracle_precision = 10**(30 - long_decimal_factor)

            long_output = self._get_claimable_fee_amount(
                market_key,
                self._long_token_address
            )

            prices = await OraclePrices().get_recent_prices()
            long_token_price = median(
                [
                    float(
                        prices[self._long_token_address].max_price_full
                    ) / oracle_precision,
                    float(
                        prices[self._long_token_address].min_price_full
                    ) / oracle_precision
                ]
            )

            long_token_price_list.append(long_token_price)
            long_precision_list.append(long_precision)

            short_output = self._get_claimable_fee_amount(
                market_key,
                self._short_token_address
            )

            # add the uncalled web3 objects to list
            long_output_list = long_output_list + [long_output]
            short_output_list = short_output_list + [short_output]

            # add the market symbol to a list to use to map to dictionary later
            mapper.append(market_symbol)

        # feed the uncalled web3 objects into threading function
        long_threaded_output = await asyncio.gather(*long_output_list)
        short_threaded_output = await asyncio.gather(*short_output_list)

        for (
            long_claimable_fees,
            short_claimable_fees,
            long_precision,
            long_token_price,
            token_symbol
        ) in zip(
            long_threaded_output,
            short_threaded_output,
            long_precision_list,
            long_token_price_list,
            mapper
        ):
            # convert raw outputs into USD value
            long_claimable_usd = (
                long_claimable_fees / long_precision
            ) * long_token_price

            # TODO - currently all short fees are collected in USDC which is
            # 6 decimals
            short_claimable_usd = short_claimable_fees / (10 ** 6)

            if "2" in token_symbol:
                short_claimable_usd = 0

            logging.info(f"Token: {token_symbol}")

            logging.info(
                f"""Long Claimable Fees:
                 ${numerize(long_claimable_usd)}"""
            )

            logging.info(
                f"""Short Claimable Fees:
                 ${numerize(short_claimable_usd)}"""
            )

            total_fees += long_claimable_usd + short_claimable_usd

        return {'total_fees': total_fees,
                "parameter": "total_fees"}

    async def _get_claimable_fee_amount(
        self, market_address: str, token_address: str
    ):
        """
        For a given market and long/short side of the pool get the raw output
        for pending fees

        Parameters
        ----------
        market_address : str
            addess of the GMX market.
        token_address : str
            address of either long or short collateral token.

        Returns
        -------
        claimable_fee : web3 datastore obj
            uncalled obj of the datastore contract.

        """

        # create hashed key to query the datastore
        claimable_fees_amount_hash_data = claimable_fee_amount_key(
            market_address,
            token_address
        )

        claimable_fee = await datastore.get_uint(
            claimable_fees_amount_hash_data
        ).get()

        return claimable_fee
