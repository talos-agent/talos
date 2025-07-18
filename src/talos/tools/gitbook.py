from langchain.tools import tool
import os
import requests

class GitBook:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {os.environ['GITBOOK_API_KEY']}"})

    @tool
    def read_page(self, page_url: str) -> str:
        """
        Reads a GitBook page.
        """
        response = self.session.get(page_url)
        response.raise_for_status()
        return response.text

    @tool
    def update_page(self, page_url: str, content: str) -> None:
        """
        Updates a GitBook page.
        """
        response = self.session.put(page_url, json={"content": content})
        response.raise_for_status()

gitbook_tools = GitBook()
read_page = gitbook_tools.read_page
update_page = gitbook_tools.update_page
