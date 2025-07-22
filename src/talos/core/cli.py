from __future__ import annotations

import os

import typer
from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.core.router import Router


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


if __name__ == "__main__":
    typer.run(main)
