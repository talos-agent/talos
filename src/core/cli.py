import os

from src.core.main_agent import MainAgent
from src.disciplines.proposals.models import RunParams


def main() -> None:
    """
    The main entry point for the Treasury Agent CLI.
    """
    agent = MainAgent(
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
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
