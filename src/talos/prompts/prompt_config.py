from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class PromptSelector(BaseModel, ABC):
    """Abstract base for prompt selection strategies."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    def select_prompts(self, context: Dict[str, Any]) -> List[str]:
        """Select prompt names based on context."""
        pass


class ConditionalPromptSelector(PromptSelector):
    """Select prompts based on conditional logic."""
    
    conditions: Dict[str, str]
    default_prompt: Optional[str] = None
    
    def select_prompts(self, context: Dict[str, Any]) -> List[str]:
        """Select prompts based on context conditions."""
        for condition_key, prompt_name in self.conditions.items():
            if context.get(condition_key):
                return [prompt_name]
        
        if self.default_prompt:
            return [self.default_prompt]
        return []


class StaticPromptSelector(PromptSelector):
    """Static list of prompt names (backward compatibility)."""
    
    prompt_names: List[str]
    
    def select_prompts(self, context: Dict[str, Any]) -> List[str]:
        """Return static prompt names."""
        return self.prompt_names


class PromptConfig(BaseModel):
    """Declarative prompt configuration."""
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    selector: PromptSelector
    variables: Dict[str, Any] = {}
    transformations: Dict[str, str] = {}
    
    def get_prompt_names(self, context: Dict[str, Any]) -> List[str]:
        """Get prompt names based on configuration and context."""
        return self.selector.select_prompts(context)
