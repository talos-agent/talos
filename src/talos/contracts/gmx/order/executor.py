from eth_typing import HexStr, HexAddress

from ..utils.gas import get_gas_limits
from .order import Order
from ..types.orders import OrderType


class OrderExecutor(Order):
    """
    Open a buy order
    Extends base Order class
    """

    async def execute(self, order_type: OrderType = OrderType.MarketIncrease) -> HexStr:
        await self.determine_gas_limits()
        return await self.execute_order(order_type=order_type)

    async def determine_gas_limits(self) -> None:
        self._gas_limits = await get_gas_limits()
        self._gas_limits_order_type = self._gas_limits.increase_order

    @classmethod
    async def calculate_initial_collateral_tokens(cls, size_delta_usd: float, leverage: int, start_token_address: HexAddress):
        """
        Calculate the amount of tokens collateral from the USD value
        """
        from ..getters.prices import OraclePrices
        from ..utils import median, get_tokens_address_dict

        collateral_usd = size_delta_usd / leverage

        prices = await OraclePrices().get_recent_prices()
        price = median(
            [
                float(prices[start_token_address].max_price_full),
                float(prices[start_token_address].min_price_full),
            ]
        )

        address_dict = await get_tokens_address_dict()
        oracle_factor = address_dict[start_token_address].decimals - 30

        amount = collateral_usd / (price * 10**oracle_factor)

        decimal = address_dict[start_token_address].decimals
        scaled_amount = int(amount * 10**decimal)

        return scaled_amount

    async def get_price(self, token_address: HexAddress) -> float:
        from ..getters.prices import OraclePrices
        from ..utils import median

        prices = await OraclePrices().get_recent_prices()
        return median([float(prices[token_address].max_price_full), float(prices[token_address].min_price_full)])
