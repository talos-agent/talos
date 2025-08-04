from __future__ import annotations

import asyncio
import base64
import os
from typing import Optional

import typer
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from nacl.public import PublicKey, SealedBox

from talos.cli.arbiscan import arbiscan_app
from talos.cli.contracts import contracts_app
from talos.cli.daemon import TalosDaemon
from talos.cli.dataset import dataset_app
from talos.cli.github import github_app
from talos.cli.memory import memory_app
from talos.cli.proposals import proposals_app
from talos.cli.twitter import twitter_app
from talos.core.main_agent import MainAgent
from talos.database.utils import cleanup_temporary_users, get_user_stats
from talos.services.key_management import KeyManagement
from talos.settings import OpenAISettings

app = typer.Typer()
app.add_typer(twitter_app, name="twitter")
app.add_typer(proposals_app, name="proposals")
app.add_typer(github_app, name="github")
app.add_typer(memory_app, name="memory")
app.add_typer(dataset_app, name="dataset")
app.add_typer(arbiscan_app, name="arbiscan")
app.add_typer(contracts_app, name="contracts")


@app.callback()
def callback(
    ctx: typer.Context,
    verbose: int = typer.Option(
        0, "--verbose", "-v", count=True, help="Enable verbose output. Use -v for basic, -vv for detailed."
    ),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User identifier for conversation tracking."),
    use_database: bool = typer.Option(
        True, "--use-database", help="Use database for conversation storage instead of files."
    ),
):
    """
    The main entry point for the Talos agent.
    """
    pass


@app.command(name="main")
def main_command(
    query: Optional[str] = typer.Argument(None, help="The query to send to the agent."),
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4o",
    temperature: float = 0.0,
    verbose: int = typer.Option(
        0, "--verbose", "-v", count=True, help="Enable verbose output. Use -v for basic, -vv for detailed."
    ),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User identifier for conversation tracking."),
    use_database: bool = typer.Option(
        True, "--use-database", help="Use database for conversation storage instead of files."
    ),
) -> None:
    """
    The main entry point for the Talos agent.
    """
    if not os.path.exists(prompts_dir):
        raise FileNotFoundError(f"Prompts directory not found at {prompts_dir}")

    OpenAISettings()

    # Create the main agent
    model = ChatOpenAI(model=model_name, temperature=temperature)
    main_agent = MainAgent(
        prompts_dir=prompts_dir,
        model=model,
        schema=None,
        user_id=user_id,
        use_database_memory=use_database,
        verbose=verbose,
    )

    if not user_id and use_database:
        print(f"Generated temporary user ID: {main_agent.user_id}")

    if query:
        # Run the agent
        result = main_agent.run(query)
        if isinstance(result, AIMessage):
            print(result.content)
        else:
            print(result)
        return

    # Interactive mode
    print("Entering interactive mode. Type 'exit' to quit.")
    while True:
        try:
            user_input = input(">> ")
            if user_input.lower() == "exit":
                break
            result = main_agent.run(user_input)
            if isinstance(result, AIMessage):
                print(result.content)
            else:
                print(result)
        except KeyboardInterrupt:
            break


@app.command()
def generate_keys(key_dir: str = ".keys"):
    """
    Generates a new RSA key pair.
    """
    km = KeyManagement(key_dir=key_dir)
    km.generate_keys()
    print(f"Keys generated in {key_dir}")


@app.command()
def get_public_key(key_dir: str = ".keys"):
    """
    Gets the public key.
    """
    km = KeyManagement(key_dir=key_dir)
    print(km.get_public_key())


@app.command()
def encrypt(data: str, public_key_file: str):
    """
    Encrypts a message.
    """
    with open(public_key_file, "rb") as f:
        public_key = f.read()

    sealed_box = SealedBox(PublicKey(public_key))
    encrypted = sealed_box.encrypt(data.encode())
    print(base64.b64encode(encrypted).decode())


@app.command()
def decrypt(encrypted_data: str, key_dir: str = ".keys"):
    """
    Decrypts a message.
    """
    km = KeyManagement(key_dir=key_dir)
    decoded_data = base64.b64decode(encrypted_data)
    print(km.decrypt(decoded_data))


@app.command()
def daemon(
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4o",
    temperature: float = 0.0,
) -> None:
    """
    Run the Talos agent in daemon mode for continuous operation with scheduled jobs.
    """
    daemon = TalosDaemon(prompts_dir=prompts_dir, model_name=model_name, temperature=temperature)
    asyncio.run(daemon.run())


@app.command()
def cleanup_users(
    older_than_hours: int = typer.Option(
        24, "--older-than", help="Remove temporary users inactive for this many hours."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without actually deleting."),
) -> None:
    """
    Clean up temporary users and their conversation data.
    """
    if dry_run:
        stats = get_user_stats()
        print("Current database stats:")
        print(f"  Total users: {stats['total_users']}")
        print(f"  Permanent users: {stats['permanent_users']}")
        print(f"  Temporary users: {stats['temporary_users']}")
        print(f"\nWould clean up temporary users inactive for {older_than_hours} hours.")
        print("Use --no-dry-run to actually perform the cleanup.")
    else:
        count = cleanup_temporary_users(older_than_hours)
        print(f"Cleaned up {count} temporary users and their conversation data.")


@app.command()
def db_stats() -> None:
    """
    Show database statistics.
    """
    stats = get_user_stats()
    print("Database Statistics:")
    print(f"  Total users: {stats['total_users']}")
    print(f"  Permanent users: {stats['permanent_users']}")
    print(f"  Temporary users: {stats['temporary_users']}")

    if stats["total_users"] > 0:
        temp_percentage = (stats["temporary_users"] / stats["total_users"]) * 100
        print(f"  Temporary user percentage: {temp_percentage:.1f}%")


if __name__ == "__main__":
    app()
