"""LLM-based memory combining utility for intelligent memory fusion."""

import os
from typing import Union

from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager


class MemoryCombiner:
    """Utility for combining similar memories using LLM-based intelligent fusion."""
    
    def __init__(self, model: str = "gpt-4o-mini", verbose: Union[bool, int] = False):
        api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(model=model, api_key=SecretStr(api_key) if api_key else None)
        self.prompt_manager = FilePromptManager("src/talos/prompts")
        self.verbose = verbose
        
    def _get_verbose_level(self) -> int:
        """Convert verbose to integer level for backward compatibility."""
        if isinstance(self.verbose, bool):
            return 1 if self.verbose else 0
        return max(0, min(2, self.verbose))
    
    def combine_memories(self, existing_memory: str, new_memory: str) -> str:
        """
        Combine two similar memories into a single coherent memory using LLM.
        
        Args:
            existing_memory: The existing memory description
            new_memory: The new memory description to combine
            
        Returns:
            Combined memory description as a single coherent sentence
        """
        try:
            prompt = self.prompt_manager.get_prompt("memory_combiner_prompt")
            if not prompt:
                if self._get_verbose_level() >= 1:
                    print("\033[33m⚠️ Memory combiner prompt not found, falling back to concatenation\033[0m")
                return f"{existing_memory}; {new_memory}"
            
            prompt_template = PromptTemplate(
                template=prompt.template,
                input_variables=prompt.input_variables,
            )
            
            chain = prompt_template | self.llm
            response = chain.invoke({
                "existing_memory": existing_memory,
                "new_memory": new_memory
            })
            
            combined = str(response.content).strip() if response.content else ""
            if self._get_verbose_level() >= 1:
                print(f"\033[36m🤖 LLM combined memories: {combined}\033[0m")
            
            return combined if combined else f"{existing_memory}; {new_memory}"
            
        except Exception as e:
            if self._get_verbose_level() >= 1:
                print(f"\033[33m⚠️ LLM memory combining failed ({e}), falling back to concatenation\033[0m")
            return f"{existing_memory}; {new_memory}"
