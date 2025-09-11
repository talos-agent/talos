from eth_typing import HexStr

from ..utils.gas import get_gas_limits
from .order import Order


class IncreaseOrder(Order):
    """
    Open a buy order
    Extends base Order class
    """

    async def execute(self) -> HexStr:
        await self.determine_gas_limits()
        return await self.execute_order(is_open=True)

    async def determine_gas_limits(self) -> None:
        self._gas_limits = await get_gas_limits()
        self._gas_limits_order_type = self._gas_limits.increase_order
