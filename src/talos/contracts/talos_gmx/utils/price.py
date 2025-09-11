from ..constants import PRECISION
from ..contracts.synthetics_reader import ExecutionPriceParams, synthetics_reader


async def get_execution_price_and_price_impact(
    params: ExecutionPriceParams,
    decimals: int,
):
    """
    Get the execution price and price impact for a position

    Parameters
    ----------
    chain : str
        arbitrum or avalanche.
    params : dict
        dictionary of the position parameters.
    decimals : int
        number of decimals of the token being traded eg ETH == 18.

    """
    output = await synthetics_reader.get_execution_price(
        params
    ).get()

    return {
        'execution_price': output.execution_price / 10**(PRECISION - decimals),
        'price_impact_usd': output.price_impact_usd / 10**PRECISION,
    }
