from __future__ import annotations

import requests

from talos.tools.base import BaseTool


class ArchivePhTool(BaseTool):
    def __init__(self) -> None:
        super().__init__(
            name="archive_ph",
            description="A tool for archiving web pages using archive.ph.",
        )

    def _run(self, url: str) -> str:
        try:
            response = requests.post("https://archive.ph/submit/", data={"url": url})  # type: ignore
            response.raise_for_status()
            if response.url:
                return response.url
            return "Error: Could not retrieve the archive URL."
        except requests.exceptions.RequestException as e:
            return f"An error occurred: {e}"
