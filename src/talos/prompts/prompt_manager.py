from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING

from langchain_core.messages import BaseMessage

from talos.prompts.prompt import Prompt

if TYPE_CHECKING:
    from talos.prompts.prompt_config import PromptConfig


class PromptManager(ABC):
    """
    An abstract base class for a prompt manager.
    """

    @abstractmethod
    def get_prompt(self, name: str | list[str]) -> Prompt | None:
        """
        Gets a prompt by name.
        """
        pass

    @abstractmethod
    def get_prompt_with_config(self, config: PromptConfig, context: Dict[str, Any]) -> Prompt | None:
        """
        Gets prompts using declarative configuration and context.
        """
        pass
    
    def apply_variable_transformations(self, template: str, variables: Dict[str, Any], transformations: Dict[str, str]) -> str:
        """
        Apply variable transformations to template.
        """
        transformed_vars = variables.copy()
        for var_name, transformation in transformations.items():
            if var_name in transformed_vars:
                if transformation == "uppercase":
                    transformed_vars[var_name] = str(transformed_vars[var_name]).upper()
                elif transformation == "lowercase":
                    transformed_vars[var_name] = str(transformed_vars[var_name]).lower()
        
        return template.format(**transformed_vars)

    def update_prompt_template(self, history: list[BaseMessage]):
        """
        Updates the prompt template based on the conversation history.
        """
        pass
