import os

from langchain_openai import ChatOpenAI
from pydantic.types import SecretStr

from talos.core.main_agent import MainAgent
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.core.router import Router


def main() -> None:
    """
    The main entry point for the Treasury Agent CLI.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        api_key=SecretStr(os.environ.get("OPENAI_API_KEY", "")),
    )
    # Get the absolute path to the prompts directory.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(current_dir, "..", "prompts")
    agent = MainAgent(
        model=llm,
        prompts_dir=prompts_dir,
        prompt_manager=FilePromptManager(prompts_dir=prompts_dir),
        schema=None,
        router=Router(services=[]),
    )

    print("Treasury Agent CLI (type 'exit' to quit)")
    while True:
        query = input("> ")
        if query.lower() == "exit":
            break

        response = agent.run(query)
        print(response)


if __name__ == "__main__":
    main()
