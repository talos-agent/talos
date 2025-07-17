import requests
# type: ignore
from pinata_python.pinata import Pinata


class IPFSUtils:
    def __init__(self, pinata_api_key: str, pinata_secret_api_key: str):
        self.pinata = Pinata(pinata_api_key, pinata_secret_api_key)

    def publish(self, file_path: str) -> str:
        """
        Publishes a file to IPFS and pins it using Pinata.

        :param file_path: The path to the file to publish.
        :return: The IPFS hash of the published file.
        """
        response = self.pinata.pin_file_to_ipfs(file_path)
        return response["IpfsHash"]

    def read(self, ipfs_hash: str) -> bytes:
        """
        Reads a file from IPFS.

        :param ipfs_hash: The IPFS hash of the file to read.
        :return: The content of the file as bytes.
        """
        # The Pinata SDK doesn't have a direct read method,
        # so we'll need to use a public gateway for now.
        response = requests.get(f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}")
        response.raise_for_status()
        return response.content
