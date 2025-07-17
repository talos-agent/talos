import ipfshttpclient


class IPFSUtils:
    def __init__(self, addr: str = "/dns/localhost/tcp/5001/http"):
        self.client = ipfshttpclient.connect(addr)

    def publish(self, file_path: str) -> str:
        """
        Publishes a file to IPFS.

        :param file_path: The path to the file to publish.
        :return: The IPFS hash of the published file.
        """
        res = self.client.add(file_path)
        return res["Hash"]

    def read(self, ipfs_hash: str) -> bytes:
        """
        Reads a file from IPFS.

        :param ipfs_hash: The IPFS hash of the file to read.
        :return: The content of the file as bytes.
        """
        return self.client.cat(ipfs_hash)
