from eth_abi import encode
from eth_hash.auto import keccak


def create_hash(data_type_list: list, data_value_list: list):
    """
    Create a keccak hash using a list of strings corresponding to data types
    and a list of the values the data types match

    Parameters
    ----------
    data_type_list : list
        list of data types as strings.
    data_value_list : list
        list of values as strings.

    Returns
    -------
    bytes
        encoded hashed key .

    """
    byte_data = encode(data_type_list, data_value_list)
    return keccak(byte_data)


def create_hash_string(string: str):
    """
    Value to hash

    Parameters
    ----------
    string : str
        string to hash.

    Returns
    -------
    bytes
        hashed string.

    """
    return create_hash(["string"], [string])
