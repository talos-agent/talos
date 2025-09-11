import httpx


async def get_tokens_address_dict() -> dict:
    """
    Query the GMX infra api for to generate dictionary of tokens available on v2

    Parameters
    ----------
    chain : str
        avalanche of arbitrum.

    Returns
    -------
    token_address_dict : dict
        dictionary containing available tokens to trade on GMX.

    """
    url = "https://arbitrum-api.gmxinfra.io/tokens"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            token_infos = response.json()['tokens']
        else:
            print(f"Error: {response.status_code}")
    except httpx.RequestError as e:
        print(f"Error: {e}")

    token_address_dict = {}

    for token_info in token_infos:
        token_address_dict[token_info['address']] = token_info

    return token_address_dict


if __name__ == "__main__":
    import asyncio

    result = asyncio.run(get_tokens_address_dict())
    print(result)
