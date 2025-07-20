import os

from langchain_openai import ChatOpenAI
from pydantic.types import SecretStr

from talos.core.main_agent import MainAgent
from talos.services.proposals.models import RunParams


def main() -> None:
    """
    The main entry point for the Treasury Agent CLI.
    """
    llm = ChatOpenAI(
        model="gpt-3.5-turbo-0125",
        temperature=0.0,
        api_key=SecretStr(os.environ.get("OPENAI_API_KEY", "")),
    )
    agent = MainAgent(
        llm=llm,
        prompts_dir="prompts",
    )

    print("Treasury Agent CLI (type 'exit' to quit)")
    while True:
        query = input("> ")
        if query.lower() == "exit":
            break

        response = agent.run(query, **RunParams().model_dump())
        print(response)


if __name__ == "__main__":
    main()
