import os
import typer
from langchain_openai import ChatOpenAI

from talos.skills.proposals import ProposalsSkill

proposals_app = typer.Typer()


@proposals_app.command("eval")
def eval_proposal(
    filepath: str = typer.Option(..., "--file", "-f", help="Path to the proposal file."),
    model_name: str = "gpt-4o",
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
