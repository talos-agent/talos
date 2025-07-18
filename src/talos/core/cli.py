import os

from talos.core.main_agent import MainAgent
from talos.disciplines.proposals.models import RunParams
from langchain_openai import OpenAI


def main() -> None:
    """
    The main entry point for the Treasury Agent CLI.
    """
    llm = OpenAI(
        model="text-davinci-003",
        temperature=0.0,
        api_key=os.environ.get("OPENAI_API_KEY", ""),
    )
    agent = MainAgent(
        llm=llm,
        pinata_api_key=os.environ.get("PINATA_API_KEY", ""),
        pinata_secret_api_key=os.environ.get("PINATA_SECRET_API_KEY", ""),
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
