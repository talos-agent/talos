from pydantic import BaseModel
from eth_rpc.types import primitives


class GasLimits(BaseModel):
    deposit: primitives.uint256
    withdraw: primitives.uint256
    single_swap: primitives.uint256
    swap_order: primitives.uint256
    increase_order: primitives.uint256
    decrease_order: primitives.uint256
    estimated_fee_base_gas_limit: primitives.uint256
    estimated_fee_multiplier_factor: primitives.uint256
