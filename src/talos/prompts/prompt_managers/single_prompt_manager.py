from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager

if TYPE_CHECKING:
    from talos.prompts.prompt_config import PromptConfig


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

    def get_prompt_with_config(self, config: PromptConfig, context: Dict[str, Any]) -> Prompt | None:
        """
        Gets prompts using declarative configuration and context.
        """
        prompt_names = config.get_prompt_names(context)
        if not prompt_names:
            return None
            
        if len(prompt_names) > 1:
            raise ValueError("SinglePromptManager does not support multiple prompt concatenation.")
            
        enhanced_template = self.prompt.template
        if config.variables or config.transformations:
            try:
                enhanced_template = self.apply_variable_transformations(
                    self.prompt.template, 
                    {**context, **config.variables}, 
                    config.transformations
                )
            except KeyError:
                pass
                
        return Prompt(
            name=f"configured_{self.prompt.name}",
            template=enhanced_template,
            input_variables=self.prompt.input_variables
        )
