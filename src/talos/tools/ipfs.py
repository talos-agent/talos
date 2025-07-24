from enum import Enum

import ipfshttpclient
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class IpfsToolName(str, Enum):
    ADD_CONTENT = "add_content"
    GET_CONTENT = "get_content"


class IpfsToolArgs(BaseModel):
    tool_name: IpfsToolName = Field(..., description="The name of the tool to run")
    content: str | None = Field(None, description="The content to add to IPFS")
    hash: str | None = Field(None, description="The hash of the content to get from IPFS")


class IpfsTool(BaseTool):
    name: str = "ipfs_tool"
    description: str = "Provides tools for interacting with IPFS."
    args_schema: type[BaseModel] = IpfsToolArgs

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
