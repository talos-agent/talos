from __future__ import annotations

import os
from typing import List, Optional

import typer
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.core.router import Router
from talos.services.key_management import KeyManagement
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


@app.callback()
def callback(ctx: typer.Context, verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output.")):
    """
    The main entry point for the Talos agent.
    """
    if ctx.invoked_subcommand is None:
        main(query=None, verbose=verbose)


@app.command()
def main(
    query: Optional[str] = typer.Argument(None, help="The query to send to the agent."),
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4",
    temperature: float = 0.0,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
) -> None:
    """
    The main entry point for the Talos agent.
    """
    if not os.path.exists(prompts_dir):
        raise FileNotFoundError(f"Prompts directory not found at {prompts_dir}")

    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    # Create the main agent
    model = ChatOpenAI(model=model_name, temperature=temperature)
    router = Router([], [])
    main_agent = MainAgent(
        prompts_dir=prompts_dir,
        model=model,
        router=router,
        schema=None,
    )

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
    history: List[BaseMessage] = []
    while True:
        try:
            user_input = input(">> ")
            if user_input.lower() == "exit":
                break
            result = main_agent.run(user_input, history=history)
            history.append(HumanMessage(content=user_input))
            if isinstance(result, AIMessage):
                history.append(AIMessage(content=result.content))
            else:
                history.append(AIMessage(content=str(result)))
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


if __name__ == "__main__":
    app()
