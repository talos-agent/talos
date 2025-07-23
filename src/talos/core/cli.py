from __future__ import annotations

import os
from typing import List, Optional

import typer
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.core.router import Router
from talos.services.key_management import KeyManagement

app = typer.Typer(invoke_without_command=True)


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


if __name__ == "__main__":
    app()
