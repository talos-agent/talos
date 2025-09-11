from ..contracts.synthetics_reader.types import ReaderUtilsMarketInfo


def apply_factor(value: int, factor: int):
    return value * factor / 10**30


def get_funding_factor_per_period(
    market_info: ReaderUtilsMarketInfo,
    is_long: bool,
    period_in_seconds: int,
    long_interest_usd: int,
    short_interest_usd: int,
) -> int:
    """
    For a given market, calculate the funding factor for a given period

    Parameters
    ----------
    market_info : dict
        market parameters returned from the reader contract.
    is_long : bool
        direction of the position.
    period_in_seconds : int
        Want percentage rate we want to output to be in.
    long_interest_usd : int
        expanded decimal long interest.
    short_interest_usd : int
        expanded decimal short interest.

    """

    funding_factor_per_second = (
        market_info.next_funding.funding_factor_per_second * 10**-28
    )

    long_pays_shorts = market_info.next_funding.longs_pay_shorts

    if is_long:
        is_larger_side = long_pays_shorts
    else:
        is_larger_side = not long_pays_shorts

    if is_larger_side:
        factor_per_second = funding_factor_per_second * -1
    else:
        if long_pays_shorts:
            larger_interest_usd = long_interest_usd
            smaller_interest_usd = short_interest_usd

        else:
            larger_interest_usd = short_interest_usd
            smaller_interest_usd = long_interest_usd

        if smaller_interest_usd > 0:
            ratio = larger_interest_usd * 10**30 / smaller_interest_usd

        else:
            ratio = 0

        factor_per_second = apply_factor(ratio, funding_factor_per_second)

    return factor_per_second * period_in_seconds
