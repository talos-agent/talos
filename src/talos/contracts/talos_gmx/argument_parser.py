import asyncio

import numpy as np

from .getters.prices import OraclePrices
from .getters.markets import Markets
from .utils import get_tokens_address_dict, determine_swap_route


class OrderArgumentParser:
    def __init__(self, is_increase: bool = False, is_decrease: bool = False, is_swap: bool = False):
        self.parameters_dict = None
        self.is_increase = is_increase
        self.is_decrease = is_decrease
        self.is_swap = is_swap

        self._markets = Markets()
        self.market_info = None

        if is_increase:
            self.required_keys = [
                "chain",
                "index_token_address",
                "market_key",
                "start_token_address",
                "collateral_address",
                "swap_path",
                "is_long",
                "size_delta_usd",
                "initial_collateral_delta",
                "slippage_percent"
            ]

        if is_decrease:
            self.required_keys = [
                "chain",
                "index_token_address",
                "market_key",
                "start_token_address",
                "collateral_address",
                "is_long",
                "size_delta_usd",
                "initial_collateral_delta",
                "slippage_percent"
            ]

        if is_swap:
            self.required_keys = [
                "chain",
                "start_token_address",
                "out_token_address",
                "initial_collateral_delta",
                "swap_path",
                "slippage_percent"
            ]

        self.missing_base_key_methods = {
            "index_token_address": self._handle_missing_index_token_address,
            "market_key": self._handle_missing_market_key,
            "start_token_address": self._handle_missing_start_token_address,
            "out_token_address": self._handle_missing_out_token_address,
            "collateral_address": self._handle_missing_collateral_address,
            "swap_path": self._handle_missing_swap_path,
            "is_long": self._handle_missing_is_long,
            "slippage_percent": self._handle_missing_slippage_percent
        }

    async def load_markets(self):
        await self._markets.load_info()
        self.market_info = self._markets.info

    async def process_parameters_dictionary(self, parameters_dict) -> dict:
        missing_keys = self._determine_missing_keys(parameters_dict)

        self.parameters_dict = parameters_dict

        for missing_key in missing_keys:
            if missing_key in self.missing_base_key_methods:
                if asyncio.iscoroutinefunction(self.missing_base_key_methods[missing_key]):
                    await self.missing_base_key_methods[missing_key]()
                else:
                    self.missing_base_key_methods[missing_key]()

        if not self.is_swap:
            await self.calculate_missing_position_size_info_keys()
            await self._check_if_max_leverage_exceeded()

        if self.is_increase:
            if await self._calculate_initial_collateral_usd() < 2:
                raise Exception("Position size must be backed by >$2 of collateral!")

        await self._format_size_info()

        return self.parameters_dict

    def _determine_missing_keys(self, parameters_dict) -> list[str]:
        """
        Compare keys in the supposed dictionary to a list of keys which are required to create an
        order

        Parameters
        ----------
        parameters_dict : dict
            user suppled dictionary of parameters to create order.

        """
        return [key for key in self.required_keys if key not in parameters_dict]

    async def _handle_missing_index_token_address(self):
        """
        Will trigger if index token address is missing. Can be determined if index token symbol is
        found, but will raise an exception if that cant be found either
        """

        try:
            token_symbol = self.parameters_dict['index_token_symbol']

            # Exception for tickers api
            if token_symbol == "BTC":
                token_symbol = "WBTC.b"
        except KeyError:
            raise Exception("Index Token Address and Symbol not provided!")

        self.parameters_dict['index_token_address'] = self.find_key_by_symbol(
            await get_tokens_address_dict(),
            token_symbol
        )

    def _handle_missing_market_key(self):
        """
        Will trigger if market key is missing. Can be determined from index token address.
        """

        index_token_address = self.parameters_dict['index_token_address']

        if index_token_address == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
            index_token_address = "0x47904963fc8b2340414262125aF798B9655E58Cd"

        # use the index token address to find the market key from get_available_markets
        self.parameters_dict['market_key'] = self.find_market_key_by_index_address(
            self.market_info,
            index_token_address
        )

    async def _handle_missing_start_token_address(self):
        """
        Will trigger if start token address is missing. Can be determined if start token symbol is
        found, but will raise an exception if that cant be found either.
        """

        try:
            start_token_symbol = self.parameters_dict['start_token_symbol']

            # Exception for tickers api
            if start_token_symbol == "BTC":
                self.parameters_dict[
                    'start_token_address'
                ] = "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"
                return

        except KeyError:
            raise Exception("Start Token Address and Symbol not provided!")

        # search the known tokens for a contract address using the user supplied symbol
        self.parameters_dict['start_token_address'] = self.find_key_by_symbol(
            await get_tokens_address_dict(),
            start_token_symbol,
        )

    async def _handle_missing_out_token_address(self):
        """
        Will trigger if start token address is missing. Can be determined if start token symbol is
        found, but will raise an exception if that cant be found either.
        """

        try:
            start_token_symbol = self.parameters_dict['out_token_symbol']
        except KeyError:
            raise Exception("Out Token Address and Symbol not provided!")

        # search the known tokens for a contract address using the user supplied symbol
        self.parameters_dict['out_token_address'] = self.find_key_by_symbol(
            await get_tokens_address_dict(),
            start_token_symbol
        )

    async def _handle_missing_collateral_address(self):
        """
        Will trigger if collateral address is missing. Can be determined if collateral token symbol
        is found, but will raise an exception if that cant be found either
        """

        try:
            collateral_token_symbol = self.parameters_dict['collateral_token_symbol']

            # Exception for tickers api
            if collateral_token_symbol == "BTC":
                self.parameters_dict[
                    'collateral_address'
                ] = "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"
                return
        except KeyError:
            raise Exception("Collateral Token Address and Symbol not provided!")

        # search the known tokens for a contract address using the user supplied symbol
        collateral_address = self.find_key_by_symbol(
            await get_tokens_address_dict(),
            collateral_token_symbol
        )

        # check if the collateral token address can be used in the requested market
        if self._check_if_valid_collateral_for_market(collateral_address) and not self.is_swap:
            self.parameters_dict['collateral_address'] = collateral_address

    def _handle_missing_swap_path(self):
        """
        Will trigger if swap path is missing. If start token is the same collateral, no swap path is
        required but otherwise will use determine_swap_route to find the path from start token to
        collateral token
        """

        if self.is_swap:
            # first get markets to supply to determine_swap_route
            markets = self.market_info

            # function returns swap route as a list [0] and a bool if there is a multi swap [1]
            self.parameters_dict['swap_path'] = determine_swap_route(
                markets,
                self.parameters_dict['start_token_address'],
                self.parameters_dict['out_token_address']
            )[0]

        # No Swap Path required to map
        elif self.parameters_dict['start_token_address'] == \
                self.parameters_dict['collateral_address']:
            self.parameters_dict['swap_path'] = []

        else:

            # first get markets to supply to determine_swap_route
            markets = self.market_info

            # function returns swap route as a list [0] and a bool if there is a multi swap [1]
            self.parameters_dict['swap_path'] = determine_swap_route(
                markets,
                self.parameters_dict['start_token_address'],
                self.parameters_dict['collateral_address']
            )[0]

    def _handle_missing_is_long(self):
        """
        Will trigger if is_long is missing from parameters dictionary, is_long must be supplied by
        user
        """

        raise Exception("Please indiciate if position is_long!")

    def _handle_missing_slippage_percent(self):
        """
        Will trigger if slippage is missing from parameters dictionary, slippage must be supplied by
        user
        """

        raise Exception("Please indiciate slippage!")

    def _check_if_valid_collateral_for_market(self, collateral_address: str):
        """
        Check is collateral address is valid in the requested market

        Parameters
        ----------
        collateral_address : str
            address of collateral token.
        """

        market_key = self.parameters_dict['market_key']

        if self.parameters_dict['market_key'] == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
            market_key = "0x47c031236e19d024b42f8AE6780E44A573170703"

        market = self.market_info[market_key]

        # if collateral address doesnt match long or short token address, no bueno
        if collateral_address == market['long_token_address'] or \
                collateral_address == market['short_token_address']:
            return True
        else:
            raise Exception("Not a valid collateral for selected market!")

    @staticmethod
    def find_key_by_symbol(input_dict: dict, search_symbol: str):
        """
        For a given token symbol, identify that key in input_dict that matches the value for
        'symbol'

        Parameters
        ----------
        input_dict : dict
            Input dictionary containing token information.
        search_symbol : str
            string of symbol we want to find the key of.
        """

        for key, value in input_dict.items():
            if value.get('symbol') == search_symbol:
                return key
        raise Exception('"{}" not a known token for GMX v2!'.format(search_symbol))

    @staticmethod
    def find_market_key_by_index_address(input_dict: dict, index_token_address: str):
        """
        For a given index token address, identify that key in input_dict that matches the value for
        'index_token_address'

        Parameters
        ----------
        input_dict : dict
            Input dictionary containing token information.
        index_token_address : str
            string of index address we want to find the key of.
        """

        for key, value in input_dict.items():
            if value.get('index_token_address') == index_token_address:
                return key
        return None

    async def calculate_missing_position_size_info_keys(self):
        """
        Look at combinations of sizesize_delta_usd_delta, intial_collateral_delta, and leverage and
        see if any missing required parameters can be calculated.
        """

        # Both size_delta_usd and initial_collateral_delta have been suppled, no issue
        if "size_delta_usd" in self.parameters_dict and \
                "initial_collateral_delta" in self.parameters_dict:
            return self.parameters_dict

        # leverage and initial_collateral_delta supplied, we can calculate size_delta_usd if missing
        elif "leverage" in self.parameters_dict and \
                "initial_collateral_delta" in self.parameters_dict and \
                "size_delta_usd" not in self.parameters_dict:

            initial_collateral_delta_usd = await self._calculate_initial_collateral_usd()

            self.parameters_dict["size_delta_usd"] = (
                self.parameters_dict["leverage"] * initial_collateral_delta_usd
            )
            return self.parameters_dict

        # size_delta_usd and leverage supplied, we can calculate initial_collateral_delta if missing
        elif "size_delta_usd" in self.parameters_dict and "leverage" in self.parameters_dict and \
                "initial_collateral_delta" not in self.parameters_dict:

            collateral_usd = self.parameters_dict["size_delta_usd"] / \
                self.parameters_dict["leverage"]

            self.parameters_dict[
                "initial_collateral_delta"
            ] = await self._calculate_initial_collateral_tokens(collateral_usd)

            return self.parameters_dict

        else:
            potential_missing_keys = '"size_delta_usd", "initial_collateral_delta", or "leverage"!'
            raise Exception(
                "Required keys are missing or provided incorrectly, please check: {}".format(
                    potential_missing_keys
                )
            )

    async def _calculate_initial_collateral_usd(self) -> float:
        """
        Calculate the USD value of the number of tokens supplied in initial collateral delta
        """

        initial_collateral_delta_amount = self.parameters_dict['initial_collateral_delta']
        prices = await OraclePrices().get_recent_prices()
        price: float = np.median(
            [float(prices[self.parameters_dict["start_token_address"]]['maxPriceFull']),
             float(prices[self.parameters_dict["start_token_address"]]['minPriceFull'])]
        )
        address_dict = await get_tokens_address_dict()
        oracle_factor: int = address_dict[self.parameters_dict["start_token_address"]]['decimals'] - 30

        return (price * 10 ** oracle_factor) * initial_collateral_delta_amount

    async def _calculate_initial_collateral_tokens(self, collateral_usd: float):
        """
        Calculate the amount of tokens collateral from the USD value

        Parameters
        ----------
        collateral_usd : float
            Dollar value of collateral.
        """

        prices = await OraclePrices().get_recent_prices()
        price = np.median(
            [float(prices[self.parameters_dict["start_token_address"]]['maxPriceFull']),
             float(prices[self.parameters_dict["start_token_address"]]['minPriceFull'])]
        )
        address_dict = await get_tokens_address_dict()
        oracle_factor = address_dict[self.parameters_dict["start_token_address"]]['decimals'] - 30

        return collateral_usd / (price * 10 ** oracle_factor)

    async def _format_size_info(self) -> None:
        """
        Convert size_delta and initial_collateral_delta to significant figures which will be
        accepted on chain
        """

        if not self.is_swap:
            # All USD numbers need to be 10**30
            self.parameters_dict["size_delta"] = int(
                self.parameters_dict["size_delta_usd"] * 10**30)

        # Each token has its a specific decimal factor that needs to be applied
        token_address_dict = await get_tokens_address_dict()
        decimal = token_address_dict[self.parameters_dict["start_token_address"]]['decimals']
        self.parameters_dict["initial_collateral_delta"] = int(
            self.parameters_dict["initial_collateral_delta"] * 10**decimal
        )

    async def _check_if_max_leverage_exceeded(self):
        """
        Using collateral tokens and size_delta calculate the requested leverage size and raise
        exception if this exceeds x100.

        """

        collateral_usd_value = await self._calculate_initial_collateral_usd()
        leverage_requested = self.parameters_dict["size_delta_usd"] / \
            collateral_usd_value

        # TODO - leverage is now a contract parameter and needs to be queried
        max_leverage = 100
        if leverage_requested > max_leverage:
            raise Exception('Leverage requested "x{:.2f}" can not exceed x100!'.format(
                leverage_requested
            ))
