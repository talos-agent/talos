import asyncio
from typing import Any, Callable

from eth_rpc.utils import to_checksum
from eth_typing import ChecksumAddress
from pydantic import BaseModel, Field, PrivateAttr

from .getters.markets import Markets
from .getters.prices import OraclePrices
from .types import Market, TokenMetadata
from .utils import determine_swap_route, get_tokens_address_dict, median


class OrderArgumentParser(BaseModel):
    parameters_dict: dict[str, Any] = Field(default_factory=dict)
    is_increase: bool = Field(default=False)
    is_decrease: bool = Field(default=False)
    is_swap: bool = Field(default=False)

    markets: Markets = Field(default_factory=Markets)

    _required_keys: list[str] = PrivateAttr()
    _missing_base_key_methods: dict[str, Callable[[], Any]] = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        if self.is_increase:
            self._required_keys = [
                "index_token_address",
                "market_key",
                "start_token_address",
                "collateral_address",
                "swap_path",
                "is_long",
                "size_delta_usd",
                "initial_collateral_delta",
                "slippage_percent",
            ]

        if self.is_decrease:
            self._required_keys = [
                "index_token_address",
                "market_key",
                "start_token_address",
                "collateral_address",
                "is_long",
                "size_delta_usd",
                "initial_collateral_delta",
                "slippage_percent",
            ]

        if self.is_swap:
            self._required_keys = [
                "start_token_address",
                "out_token_address",
                "initial_collateral_delta",
                "swap_path",
                "slippage_percent",
            ]

        self._missing_base_key_methods = {
            "start_token_address": self._handle_missing_start_token_address,
            "index_token_address": self._handle_missing_index_token_address,
            "market_key": self._handle_missing_market_key,
            "out_token_address": self._handle_missing_out_token_address,
            "collateral_address": self._handle_missing_collateral_address,
            "swap_path": self._handle_missing_swap_path,
            "is_long": self._handle_missing_is_long,
            "slippage_percent": self._handle_missing_slippage_percent,
        }

    async def process_parameters_dictionary(self, parameters_dict: dict[str, Any]) -> dict[str, Any]:
        await self.markets.load_info()

        missing_keys = self._determine_missing_keys(parameters_dict)

        self.parameters_dict = parameters_dict

        for missing_key in missing_keys:
            if missing_key in self._missing_base_key_methods:
                if asyncio.iscoroutinefunction(self._missing_base_key_methods[missing_key]):
                    await self._missing_base_key_methods[missing_key]()
                else:
                    self._missing_base_key_methods[missing_key]()

        if not self.is_swap:
            await self.calculate_missing_position_size_info_keys()
            await self._check_if_max_leverage_exceeded()

        if self.is_increase:
            if await self._calculate_initial_collateral_usd() < 2:
                raise Exception("Position size must be backed by >$2 of collateral!")

        await self._format_size_info()

        return self.parameters_dict

    def _determine_missing_keys(self, parameters_dict: dict[str, Any]) -> list[str]:
        """
        Compare keys in the supposed dictionary to a list of keys which are required to create an
        order

        Parameters
        ----------
        parameters_dict : dict
            user suppled dictionary of parameters to create order.

        """
        return [key for key in self._required_keys if key not in parameters_dict]

    async def _handle_missing_index_token_address(self) -> None:
        """
        Will trigger if index token address is missing. Can be determined if index token symbol is
        found, but will raise an exception if that cant be found either
        """

        try:
            token_symbol = self.parameters_dict["index_token_symbol"]

            # Exception for tickers api
            if token_symbol == "BTC":
                token_symbol = "WBTC.b"
        except KeyError:
            raise Exception("Index Token Address and Symbol not provided!")

        self.parameters_dict["index_token_address"] = self.find_key_by_symbol(
            await get_tokens_address_dict(), token_symbol
        )

    def _handle_missing_market_key(self) -> None:
        """
        Will trigger if market key is missing. Can be determined from index token address.
        """

        index_token_address = self.parameters_dict["index_token_address"]

        if index_token_address == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
            index_token_address = "0x47904963fc8b2340414262125aF798B9655E58Cd"

        # use the index token address to find the market key from get_available_markets
        self.parameters_dict["market_key"] = self.find_market_key_by_index_address(
            self.markets.info, index_token_address
        )

    async def _handle_missing_start_token_address(self) -> None:
        """
        Will trigger if start token address is missing. Can be determined if start token symbol is
        found, but will raise an exception if that cant be found either.
        """
        print("HANDLE MISSING START TOKEN ADDRESS")

        try:
            start_token_symbol = self.parameters_dict["start_token_symbol"]

            # Exception for tickers api
            if start_token_symbol == "BTC":
                self.parameters_dict["start_token_address"] = "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"
                return

        except KeyError:
            raise Exception("Start Token Address and Symbol not provided!")

        # search the known tokens for a contract address using the user supplied symbol
        self.parameters_dict["start_token_address"] = self.find_key_by_symbol(
            await get_tokens_address_dict(),
            start_token_symbol,
        )
        print("START TOKEN ADDRESS", self.parameters_dict["start_token_address"])

    async def _handle_missing_out_token_address(self) -> None:
        """
        Will trigger if start token address is missing. Can be determined if start token symbol is
        found, but will raise an exception if that cant be found either.
        """

        try:
            start_token_symbol = self.parameters_dict["out_token_symbol"]
        except KeyError:
            raise Exception("Out Token Address and Symbol not provided!")

        # search the known tokens for a contract address using the user supplied symbol
        self.parameters_dict["out_token_address"] = self.find_key_by_symbol(
            await get_tokens_address_dict(), start_token_symbol
        )

    async def _handle_missing_collateral_address(self) -> None:
        """
        Will trigger if collateral address is missing. Can be determined if collateral token symbol
        is found, but will raise an exception if that cant be found either
        """

        try:
            collateral_token_symbol = self.parameters_dict["collateral_token_symbol"]

            # Exception for tickers api
            if collateral_token_symbol == "BTC":
                self.parameters_dict["collateral_address"] = "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"
                return
        except KeyError:
            raise Exception("Collateral Token Address and Symbol not provided!")

        # search the known tokens for a contract address using the user supplied symbol
        collateral_str = self.find_key_by_symbol(await get_tokens_address_dict(), collateral_token_symbol)
        assert collateral_str is not None

        collateral_address = to_checksum(collateral_str)

        # check if the collateral token address can be used in the requested market
        if self._check_if_valid_collateral_for_market(collateral_address) and not self.is_swap:
            self.parameters_dict["collateral_address"] = collateral_address

    def _handle_missing_swap_path(self) -> None:
        """
        Will trigger if swap path is missing. If start token is the same collateral, no swap path is
        required but otherwise will use determine_swap_route to find the path from start token to
        collateral token
        """

        if self.is_swap:
            # function returns swap route as a list [0] and a bool if there is a multi swap [1]
            self.parameters_dict["swap_path"] = determine_swap_route(
                self.markets.info,
                self.parameters_dict["start_token_address"],
                self.parameters_dict["out_token_address"],
            )[0]

        # No Swap Path required to map
        elif self.parameters_dict["start_token_address"] == self.parameters_dict["collateral_address"]:
            self.parameters_dict["swap_path"] = []

        else:
            # function returns swap route as a list [0] and a bool if there is a multi swap [1]
            self.parameters_dict["swap_path"] = determine_swap_route(
                self.markets.info,
                self.parameters_dict["start_token_address"],
                self.parameters_dict["collateral_address"],
            )[0]

    def _handle_missing_is_long(self) -> None:
        """
        Will trigger if is_long is missing from parameters dictionary, is_long must be supplied by
        user
        """

        raise Exception("Please indiciate if position is_long!")

    def _handle_missing_slippage_percent(self) -> None:
        """
        Will trigger if slippage is missing from parameters dictionary, slippage must be supplied by
        user
        """

        raise Exception("Please indiciate slippage!")

    def _check_if_valid_collateral_for_market(self, collateral_address: ChecksumAddress) -> bool:
        """
        Check is collateral address is valid in the requested market.
        A collateral token is only valid if it is the long or short token of the market.

        Parameters
        ----------
        collateral_address : str
            address of collateral token.
        """

        market_key = self.parameters_dict["market_key"]

        if self.parameters_dict["market_key"] == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
            market_key = "0x47c031236e19d024b42f8AE6780E44A573170703"

        assert self.markets.info is not None
        market = self.markets.info[market_key]

        if collateral_address == market.long_token_address or collateral_address == market.short_token_address:
            return True
        raise Exception("Not a valid collateral for selected market!")

    @staticmethod
    def find_key_by_symbol(input_dict: dict[ChecksumAddress, TokenMetadata], search_symbol: str) -> str | None:
        """
        For a given token symbol, identify that key in input_dict that matches the value for
        'symbol'
        """

        for key, value in input_dict.items():
            if value.symbol == search_symbol:
                return key
        raise Exception('"{}" not a known token for GMX v2!'.format(search_symbol))

    @staticmethod
    def find_market_key_by_index_address(
        input_dict: dict[ChecksumAddress, Market], index_token_address: ChecksumAddress
    ) -> ChecksumAddress | None:
        """
        For a given index token address, identify that key in input_dict that matches the value for
        'index_token_address'
        """

        for key, value in input_dict.items():
            if value.index_token_address == index_token_address:
                return key
        return None

    async def calculate_missing_position_size_info_keys(self) -> dict[str, Any]:
        """
        Look at combinations of size_delta_usd_delta, intial_collateral_delta, and leverage and
        see if any missing required parameters can be calculated.
        """

        # Both size_delta_usd and initial_collateral_delta have been suppled, no issue
        if "size_delta_usd" in self.parameters_dict and "initial_collateral_delta" in self.parameters_dict:
            return self.parameters_dict

        # leverage and initial_collateral_delta supplied, we can calculate size_delta_usd if missing
        elif (
            "leverage" in self.parameters_dict
            and "initial_collateral_delta" in self.parameters_dict
            and "size_delta_usd" not in self.parameters_dict
        ):
            initial_collateral_delta_usd = await self._calculate_initial_collateral_usd()

            self.parameters_dict["size_delta_usd"] = self.parameters_dict["leverage"] * initial_collateral_delta_usd
            return self.parameters_dict

        # size_delta_usd and leverage supplied, we can calculate initial_collateral_delta if missing
        elif (
            "size_delta_usd" in self.parameters_dict
            and "leverage" in self.parameters_dict
            and "initial_collateral_delta" not in self.parameters_dict
        ):
            collateral_usd = self.parameters_dict["size_delta_usd"] / self.parameters_dict["leverage"]

            self.parameters_dict["initial_collateral_delta"] = await self._calculate_initial_collateral_tokens(
                collateral_usd
            )

            return self.parameters_dict
        else:
            potential_missing_keys = '"size_delta_usd", "initial_collateral_delta", or "leverage"!'
            raise Exception(
                "Required keys are missing or provided incorrectly, please check: {}".format(potential_missing_keys)
            )

    async def _calculate_initial_collateral_usd(self) -> float:
        """
        Calculate the USD value of the number of tokens supplied in initial collateral delta
        """

        initial_collateral_delta_amount = self.parameters_dict["initial_collateral_delta"]
        prices = await OraclePrices().get_recent_prices()
        price: float = median(
            [
                float(prices[self.parameters_dict["start_token_address"]].max_price_full),
                float(prices[self.parameters_dict["start_token_address"]].min_price_full),
            ]
        )
        address_dict = await get_tokens_address_dict()
        oracle_factor: int = address_dict[self.parameters_dict["start_token_address"]].decimals - 30

        return float((price * 10**oracle_factor) * initial_collateral_delta_amount)

    async def _calculate_initial_collateral_tokens(self, collateral_usd: float) -> float:
        """
        Calculate the amount of tokens collateral from the USD value
        """

        prices = await OraclePrices().get_recent_prices()
        price = median(
            [
                float(prices[self.parameters_dict["start_token_address"]].max_price_full),
                float(prices[self.parameters_dict["start_token_address"]].min_price_full),
            ]
        )
        address_dict = await get_tokens_address_dict()
        oracle_factor = address_dict[self.parameters_dict["start_token_address"]].decimals - 30

        return float(collateral_usd / (price * 10**oracle_factor))

    async def _format_size_info(self) -> None:
        """
        Convert size_delta and initial_collateral_delta to significant figures which will be
        accepted on chain
        """

        if not self.is_swap:
            # All USD numbers need to be 10**30
            self.parameters_dict["size_delta"] = int(self.parameters_dict["size_delta_usd"] * 10**30)

        # Each token has its a specific decimal factor that needs to be applied
        token_address_dict = await get_tokens_address_dict()
        decimal = token_address_dict[self.parameters_dict["start_token_address"]].decimals
        print("decimal", decimal)
        print('self.parameters_dict["initial_collateral_delta"]', self.parameters_dict["initial_collateral_delta"])
        self.parameters_dict["initial_collateral_delta"] = int(
            self.parameters_dict["initial_collateral_delta"] * 10**decimal
        )
        print('self.parameters_dict["initial_collateral_delta"]', self.parameters_dict["initial_collateral_delta"])

    async def _check_if_max_leverage_exceeded(self) -> None:
        """
        Using collateral tokens and size_delta calculate the requested leverage size and raise
        exception if this exceeds x100.
        """

        collateral_usd_value = await self._calculate_initial_collateral_usd()
        leverage_requested = self.parameters_dict["size_delta_usd"] / collateral_usd_value

        # TODO - leverage is now a contract parameter and needs to be queried
        max_leverage = 100
        if leverage_requested > max_leverage:
            raise Exception('Leverage requested "x{:.2f}" can not exceed x100!'.format(leverage_requested))
