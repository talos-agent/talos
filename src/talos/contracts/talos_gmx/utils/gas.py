from eth_rpc.networks import Arbitrum
from eth_typeshed.multicall import make_multicall

from ..contracts.datastore import datastore
from ..types.gas_limits import GasLimits
from .funding import apply_factor
from .keys import (
    decrease_order_gas_limit_key,
    deposit_gas_limit_key,
    execution_gas_fee_base_amount_key,
    execution_gas_fee_multiplier_key,
    increase_order_gas_limit_key,
    single_swap_gas_limit_key,
    swap_order_gas_limit_key,
    withdraw_gas_limit_key,
)


def get_execution_fee(gas_limits: GasLimits, estimated_gas_limit: int, gas_price: int) -> int:
    """
    Given a dictionary of gas_limits, the uncalled datastore object of a given operation, and the
    latest gas price, calculate the minimum execution fee required to perform an action

    Parameters
    ----------
    gas_limits : dict
        dictionary of uncalled datastore limit obkects.
    estimated_gas_limit : datastore_object
        the uncalled datastore object specific to operation that will be undertaken.
    gas_price : int
        latest gas price.

    """

    base_gas_limit = gas_limits.estimated_fee_base_gas_limit
    multiplier_factor = gas_limits.estimated_fee_multiplier_factor
    adjusted_gas_limit = base_gas_limit + apply_factor(estimated_gas_limit, multiplier_factor)

    return int(adjusted_gas_limit * gas_price)


async def get_gas_limits() -> GasLimits:
    """
    Given a Web3 contract object of the datstore, return a dictionary with the uncalled gas limits
    that correspond to various operations that will require the execution fee to calculated for.

    Parameters
    ----------
    datastore_object : web3 object
        contract connection.

    """
    multicall = make_multicall(Arbitrum)

    calls = [
        datastore.get_uint(deposit_gas_limit_key()),
        datastore.get_uint(withdraw_gas_limit_key()),
        datastore.get_uint(single_swap_gas_limit_key()),
        datastore.get_uint(swap_order_gas_limit_key()),
        datastore.get_uint(increase_order_gas_limit_key()),
        datastore.get_uint(decrease_order_gas_limit_key()),
        datastore.get_uint(execution_gas_fee_base_amount_key()),
        datastore.get_uint(execution_gas_fee_multiplier_key()),
    ]

    results = await multicall.execute(*calls)

    gas_limits = GasLimits(
        deposit=results[0],
        withdraw=results[1],
        single_swap=results[2],
        swap_order=results[3],
        increase_order=results[4],
        decrease_order=results[5],
        estimated_fee_base_gas_limit=results[6],
        estimated_fee_multiplier_factor=results[7],
    )

    return gas_limits
