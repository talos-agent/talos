from __future__ import annotations

import os

import typer
from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.core.router import Router
from talos.services.key_management import KeyManagement

app = typer.Typer()


@app.command()
def main(
    query: str,
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4",
    temperature: float = 0.0,
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

    # Run the agent
    result = main_agent.run(query)
    print(result)


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
def decrypt(encrypted_data: str, key_dir: str = ".keys"):
    """
    Decrypts a message.
    """
    km = KeyManagement(key_dir=key_dir)
    # The `CryptographySkill` is expecting a base64 encoded string,
    # but the KeyManagement service does the decoding.
    # We need to pass the raw encrypted data to the service.
    import base64

    decoded_data = base64.b64decode(encrypted_data)
    print(km.decrypt(decoded_data))


if __name__ == "__main__":
    app()
