from langchain.tools import tool
import ipfshttpclient

@tool
def add_content(content: str) -> str:
    """
    Adds content to IPFS.
    """
    client = ipfshttpclient.connect()
    return client.add_str(content)

@tool
def get_content(hash: str) -> str:
    """
    Gets content from IPFS.
    """
    client = ipfshttpclient.connect()
    return client.cat(hash).decode()
