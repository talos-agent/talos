from __future__ import annotations

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager


class SinglePromptManager(PromptManager):
    """
    A prompt manager that holds a single prompt.
    """

    def __init__(self, prompt: Prompt):
        self.prompt = prompt

    def get_prompt(self, name: str | list[str]) -> Prompt | None:
        """
        Gets the prompt.
        """
        if isinstance(name, list):
            raise ValueError("SinglePromptManager does not support prompt concatenation.")
        return self.prompt
