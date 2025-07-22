from duckduckgo_search import DDGS

from talos.tools.base import BaseTool


class WebSearchTool(BaseTool):
    def __init__(self):
        self.ddgs = DDGS()
        super().__init__(
            name="web_search",
            description="A tool for searching the web.",
        )

    def _run(self, query: str) -> str:
        return self.ddgs.text(query, max_results=5)
