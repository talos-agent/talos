from __future__ import annotations

from typing import Any, Dict, TYPE_CHECKING

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager

if TYPE_CHECKING:
    from talos.prompts.prompt_config import PromptConfig


class DynamicPromptManager(PromptManager):
    """
    A class to manage dynamic prompts.
    """

    def __init__(self, initial_prompt: Prompt):
        self.prompts: dict[str, Prompt] = {"default": initial_prompt}

    def get_prompt(self, name: str | list[str]) -> Prompt | None:
        """
        Gets a prompt by name.
        """
        if isinstance(name, list):
            raise ValueError("DynamicPromptManager does not support prompt concatenation.")
        return self.prompts.get(name)

    def get_prompt_with_config(self, config: PromptConfig, context: Dict[str, Any]) -> Prompt | None:
        """
        Gets prompts using declarative configuration and context.
        """
        
        prompt_names = config.get_prompt_names(context)
        if not prompt_names:
            return None
            
        if len(prompt_names) > 1:
            raise ValueError("DynamicPromptManager does not support multiple prompt concatenation.")
            
        prompt_name = prompt_names[0]
        base_prompt = self.prompts.get(prompt_name)
        if not base_prompt:
            return None
            
        enhanced_template = base_prompt.template
        if config.variables or config.transformations:
            try:
                enhanced_template = self.apply_variable_transformations(
                    base_prompt.template, 
                    {**context, **config.variables}, 
                    config.transformations
                )
            except KeyError:
                pass
                
        return Prompt(
            name=f"configured_{base_prompt.name}",
            template=enhanced_template,
            input_variables=base_prompt.input_variables
        )

    def update_prompt(self, name: str, template: str, input_variables: list[str]) -> None:
        """
        Updates a prompt.
        """
        self.prompts[name] = Prompt(name, template, input_variables)
