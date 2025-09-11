def find_dictionary_by_key_value(outer_dict: dict, key: str, value: str):
    """
    For a given dictionary, find a value which matches a set of keys

    Parameters
    ----------
    outer_dict : dict
        dictionary to filter through.
    key : str
        keys to search for.
    value : str
        required key to match.

    """
    for inner_dict in outer_dict.values():
        if key in inner_dict and inner_dict[key] == value:
            return inner_dict
    return None


def determine_swap_route(markets: dict, in_token: str, out_token: str):
    """
    Using the available markets, find the list of GMX markets required
    to swap from token in to token out

    Parameters
    ----------
    markets : dict
        dictionary of markets output by getMarketInfo.
    in_token : str
        contract address of in token.
    out_token : str
        contract address of out token.

    Returns
    -------
    list
        list of GMX markets to swap through.
    is_requires_multi_swap : TYPE
        requires more than one market to pass thru.

    """

    if in_token == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
        in_token = "0x47904963fc8b2340414262125aF798B9655E58Cd"

    if out_token == "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f":
        out_token = "0x47904963fc8b2340414262125aF798B9655E58Cd"

    if in_token == "0xaf88d065e77c8cC2239327C5EDb3A432268e5831":
        gmx_market_address = find_dictionary_by_key_value(
            markets,
            "index_token_address",
            out_token
        )['gmx_market_address']
    else:
        gmx_market_address = find_dictionary_by_key_value(
            markets,
            "index_token_address",
            in_token
        )['gmx_market_address']

    is_requires_multi_swap = False

    if out_token != "0xaf88d065e77c8cC2239327C5EDb3A432268e5831" and \
            in_token != "0xaf88d065e77c8cC2239327C5EDb3A432268e5831":
        is_requires_multi_swap = True
        second_gmx_market_address = find_dictionary_by_key_value(
            markets,
            "index_token_address",
            out_token
        )['gmx_market_address']

        return [gmx_market_address, second_gmx_market_address], is_requires_multi_swap

    return [gmx_market_address], is_requires_multi_swap
