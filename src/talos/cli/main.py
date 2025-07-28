from __future__ import annotations

import os
from typing import Optional

import typer
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.core.router import Router
from talos.services.key_management import KeyManagement
from talos.settings import OpenAISettings
from talos.skills.proposals import ProposalsSkill
from talos.skills.twitter_persona import TwitterPersonaSkill
from talos.skills.twitter_sentiment import TwitterSentimentSkill
from talos.cli.daemon import TalosDaemon

app = typer.Typer(invoke_without_command=True)
twitter_app = typer.Typer()
app.add_typer(twitter_app, name="twitter")
proposals_app = typer.Typer()
app.add_typer(proposals_app, name="proposals")


@proposals_app.command("eval")
def eval_proposal(
    filepath: str = typer.Option(..., "--file", "-f", help="Path to the proposal file."),
    model_name: str = "gpt-4",
    temperature: float = 0.0,
):
    """
    Evaluates a proposal from a file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at {filepath}")
    model = ChatOpenAI(model=model_name, temperature=temperature)
    skill = ProposalsSkill(llm=model)
    response = skill.run(filepath=filepath)
    print(response.answers[0])


@twitter_app.command()
def get_user_prompt(username: str):
    """
    Gets the general voice of a user as a structured persona analysis.
    """
    skill = TwitterPersonaSkill()
    response = skill.run(username=username)
    
    print(f"=== Twitter Persona Analysis for @{username} ===\n")
    print(f"Report:\n{response.report}\n")
    print(f"Topics: {', '.join(response.topics)}\n")
    print(f"Style: {', '.join(response.style)}")


@twitter_app.command()
def get_query_sentiment(query: str, start_time: Optional[str] = None):
    """
    Gets the general sentiment/report on a specific query.

    Args:
        query: Search query for tweets
        start_time: Optional datetime filter (ISO 8601 format, e.g., "2023-01-01T00:00:00Z")
    """
    skill = TwitterSentimentSkill()
    response = skill.run(query=query, start_time=start_time)
    if response.score is not None:
        print(f"Sentiment Score: {response.score}/100")
        print("=" * 50)
    print(response.answers[0])


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context, 
    query: Optional[str] = typer.Argument(None, help="The query to send to the agent."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output.")
):
    """
    The main entry point for the Talos agent.
    """
    if ctx.invoked_subcommand is None:
        main(query=query, verbose=verbose, user_id=None, use_database=True)


@app.command()
def main(
    query: Optional[str] = typer.Argument(None, help="The query to send to the agent."),
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4",
    temperature: float = 0.0,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User identifier for conversation tracking."),
    use_database: bool = typer.Option(True, "--use-database", help="Use database for conversation storage instead of files."),
) -> None:
    """
    The main entry point for the Talos agent.
    """
    if not os.path.exists(prompts_dir):
        raise FileNotFoundError(f"Prompts directory not found at {prompts_dir}")

    OpenAISettings()

    # Create the main agent
    model = ChatOpenAI(model=model_name, temperature=temperature)
    router = Router([], [])
    main_agent = MainAgent(
        prompts_dir=prompts_dir,
        model=model,
        router=router,
        schema=None,
        user_id=user_id,
        use_database_memory=use_database,
    )
    
    if not user_id and use_database:
        print(f"Generated temporary user ID: {main_agent.user_id}")

    if query:
        # Run the agent
        result = main_agent.run(query)
        if verbose:
            print(result)
        else:
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
            if verbose:
                print(result)
            else:
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

    import base64

    from nacl.public import PublicKey, SealedBox

    sealed_box = SealedBox(PublicKey(public_key))
    encrypted = sealed_box.encrypt(data.encode())
    print(base64.b64encode(encrypted).decode())


@app.command()
def decrypt(encrypted_data: str, key_dir: str = ".keys"):
    """
    Decrypts a message.
    """
    km = KeyManagement(key_dir=key_dir)
    import base64

    decoded_data = base64.b64decode(encrypted_data)
    print(km.decrypt(decoded_data))


@app.command()
def daemon(
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4",
    temperature: float = 0.0,
) -> None:
    """
    Run the Talos agent in daemon mode for continuous operation with scheduled jobs.
    """
    import asyncio
    
    daemon = TalosDaemon(
        prompts_dir=prompts_dir,
        model_name=model_name,
        temperature=temperature
    )
    asyncio.run(daemon.run())


@app.command()
def cleanup_users(
    older_than_hours: int = typer.Option(24, "--older-than", help="Remove temporary users inactive for this many hours."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without actually deleting."),
) -> None:
    """
    Clean up temporary users and their conversation data.
    """
    from talos.database.utils import cleanup_temporary_users, get_user_stats
    
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
    from talos.database.utils import get_user_stats
    
    stats = get_user_stats()
    print("Database Statistics:")
    print(f"  Total users: {stats['total_users']}")
    print(f"  Permanent users: {stats['permanent_users']}")
    print(f"  Temporary users: {stats['temporary_users']}")
    
    if stats['total_users'] > 0:
        temp_percentage = (stats['temporary_users'] / stats['total_users']) * 100
        print(f"  Temporary user percentage: {temp_percentage:.1f}%")


if __name__ == "__main__":
    app()
