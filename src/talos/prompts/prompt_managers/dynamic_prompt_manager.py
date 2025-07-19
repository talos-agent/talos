from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager


class DynamicPromptManager(PromptManager):
    """
    A class to manage dynamic prompts.
    """

    def __init__(self, initial_prompt: Prompt):
        self.prompts: dict[str, Prompt] = {"default": initial_prompt}

    def get_prompt(self, name: str) -> Prompt | None:
        """
        Gets a prompt by name.
        """
        return self.prompts.get(name)

    def update_prompt(self, name: str, template: str, input_variables: list[str]) -> None:
        """
        Updates a prompt.
        """
        self.prompts[name] = Prompt(name, template, input_variables)
