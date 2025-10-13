# src/talos/cli/twitch.py
from __future__ import annotations

import asyncio

import typer

from talos.tools.twitch_listener import run as run_twitch_listener

twitch_app = typer.Typer()


@twitch_app.command()
def listen(channel_name: str = typer.Argument(..., help="The name of the Twitch channel to listen to.")) -> None:
    """
    Starts the Twitch listener to monitor a channel for messages.
    """
    print(f"Starting Twitch listener for channel: {channel_name}...")
    asyncio.run(run_twitch_listener(channel_name))


if __name__ == "__main__":
    twitch_app()
