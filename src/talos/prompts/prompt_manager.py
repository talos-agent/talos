from abc import ABC, abstractmethod
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
