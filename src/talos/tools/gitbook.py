import os
import requests
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from enum import Enum

class GitBookToolName(str, Enum):
    READ_PAGE = "read_page"
    UPDATE_PAGE = "update_page"

class GitBookToolArgs(BaseModel):
    tool_name: GitBookToolName = Field(..., description="The name of the tool to run")
    page_url: str = Field(..., description="The URL of the GitBook page")
    content: str | None = Field(None, description="The content to update the page with")

class GitBookTool(BaseTool):
    name = "gitbook_tool"
    description = "Provides tools for interacting with the GitBook API."
    args_schema: type[BaseModel] = GitBookToolArgs

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {os.environ['GITBOOK_API_KEY']}"})

    def read_page(self, page_url: str) -> str:
        """
        Reads a GitBook page.
        """
        response = self.session.get(page_url)
        response.raise_for_status()
        return response.text

    def update_page(self, page_url: str, content: str) -> str:
        """
        Updates a GitBook page.
        """
        response = self.session.put(page_url, json={"content": content})
        response.raise_for_status()
        return "Page updated successfully."

    def _run(self, tool_name: str, **kwargs):
        if tool_name == "read_page":
            return self.read_page(**kwargs)
        elif tool_name == "update_page":
            return self.update_page(**kwargs)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
