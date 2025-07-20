from abc import ABC, abstractmethod

from langchain_core.messages import BaseMessage

from talos.prompts.prompt import Prompt


class PromptManager(ABC):
    """
    An abstract base class for a prompt manager.
    """

    @abstractmethod
    def get_prompt(self, name: str) -> Prompt | None:
        """
        Gets a prompt by name.
        """
        pass

    def update_prompt_template(self, history: list[BaseMessage]):
        """
        Updates the prompt template based on the conversation history.
        """
        pass
