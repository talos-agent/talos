"""
CLI commands for Perplexity service.
"""

from __future__ import annotations

from typing import Annotated

import typer

from talos.services.implementations.perplexity import PerplexityService

app = typer.Typer()


@app.command()
def search(
    query: str,
    api_key: Annotated[str, typer.Option(..., envvar="PERPLEXITY_API_KEY")] = ""
) -> None:
    """
    Searches Perplexity with the given query.
    """
    if not api_key:
        msg = ("Perplexity API key not found. "
               "Please set the PERPLEXITY_API_KEY environment variable.")
        raise typer.BadParameter(msg)

    service = PerplexityService(token=api_key)
    response = service.search(query)
    print(response)
