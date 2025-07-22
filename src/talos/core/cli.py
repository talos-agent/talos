import os
from pathlib import Path

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import BaseModel
from pydantic.types import SecretStr

from talos.core.main_agent import MainAgent
from talos.core.memory import Memory
from talos.core.router import Router
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager


def main() -> None:
    """
    The main entry point for the Treasury Agent CLI.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.0,
        api_key=SecretStr(os.environ.get("OPENAI_API_KEY", "")),
    )
    embeddings = OpenAIEmbeddings(api_key=SecretStr(os.environ.get("OPENAI_API_KEY", "")))
    # Get the absolute path to the prompts directory.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(current_dir, "..", "prompts")
    # Get the absolute path to the memory file.
    memory_path = Path(current_dir) / ".." / "memory"
    agent = MainAgent(
        model=llm,
        prompts_dir=prompts_dir,
        prompt_manager=FilePromptManager(prompts_dir=prompts_dir),
        schema=None,
        router=Router(services=[]),
        memory=Memory(
            file_path=memory_path / "memories.json",
            history_file_path=memory_path / "history.json",
            embeddings_model=embeddings,
        ),
    )

    print("Treasury Agent CLI (type 'exit' to quit)")
    while True:
        query = input("> ")
        if query.lower() == "exit":
            break

        response = agent.run(query)
        if isinstance(response, AIMessage):
            print(response.content)
        elif isinstance(response, BaseModel) and hasattr(response, "content"):
            print(response.content)  # type: ignore
        else:
            print(response)


if __name__ == "__main__":
    main()
