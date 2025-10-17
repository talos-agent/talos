from __future__ import annotations

import os
import typer

from talos.services.implementations.perplexity import PerplexityService

app = typer.Typer()


@app.command()
def search(query: str, api_key: str = typer.Option(..., envvar="PERPLEXITY_API_KEY")):
    """
    Searches Perplexity with the given query.
    """
    if not api_key:
        raise typer.BadParameter("Perplexity API key not found. Please set the PERPLEXITY_API_KEY environment variable.")

    service = PerplexityService(token=api_key)
    response = service.search(query)
    print(response)