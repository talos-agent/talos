import os
from pydantic.types import SecretStr

from talos.core.main_agent import MainAgent
from talos.services.proposals.models import RunParams
from langchain_openai import OpenAI


def main() -> None:
    """
    The main entry point for the Treasury Agent CLI.
    """
    llm = OpenAI(
        model="text-davinci-003",
        temperature=0.0,
        api_key=SecretStr(os.environ.get("OPENAI_API_KEY", "")),
    )
    agent = MainAgent(
        llm=llm,
        tools=[],
        prompts_dir="prompts",
    )

    print("Treasury Agent CLI (type 'exit' to quit)")
    while True:
        query = input("> ")
        if query.lower() == "exit":
            break

        response = agent.run(query, params=RunParams())
        print(response.answers[0].answer)


if __name__ == "__main__":
    main()
