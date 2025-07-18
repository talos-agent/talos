import ipfshttpclient
from langchain.tools import BaseTool

class IpfsTool(BaseTool):
    name = "ipfs_tool"
    description = "Provides tools for interacting with IPFS."

    def __init__(self):
        super().__init__()
        self.client = ipfshttpclient.connect()

    def add_content(self, content: str) -> str:
        """
        Adds content to IPFS.
        """
        return self.client.add_str(content)

    def get_content(self, hash: str) -> str:
        """
        Gets content from IPFS.
        """
        return self.client.cat(hash).decode()

    def _run(self, tool_name: str, **kwargs):
        if tool_name == "add_content":
            return self.add_content(**kwargs)
        elif tool_name == "get_content":
            return self.get_content(**kwargs)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
