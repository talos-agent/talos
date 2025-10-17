from __future__ import annotations

import subprocess
from pathlib import Path

import typer

app = typer.Typer()


@app.command()
def start(
    config: str = typer.Option(
        "config/sampler-config.yml",
        "--config",
        "-c",
        help="Path to the sampler config file.",
    )
):
    """
    Starts the monitoring service.
    """
    if not Path(config).exists():
        print(f"Config file not found at {config}")
        raise typer.Exit(1)

    try:
        subprocess.run(["sampler", "-c", config], check=True)
    except FileNotFoundError:
        print("Error: 'sampler' command not found.")
        print("Please install Sampler and ensure it is in your PATH.")
        print("See here for installation instructions: https://github.com/sqshq/sampler")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error running sampler: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()