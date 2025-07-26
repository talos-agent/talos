import json
import os
from typing import Dict

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager


class FilePromptManager(PromptManager):
    """
    A class to manage prompts from files with caching.
    """

    def __init__(self, prompts_dir: str):
        self.prompts_dir = prompts_dir
        self.prompts: dict[str, Prompt] = {}
        self._file_mtimes: Dict[str, float] = {}
        self.load_prompts()

    def load_prompts(self) -> None:
        """
        Loads all prompts from the prompts directory with caching based on file modification time.
        """
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".json"):
                filepath = os.path.join(self.prompts_dir, filename)
                current_mtime = os.path.getmtime(filepath)
                
                if filename in self._file_mtimes and self._file_mtimes[filename] == current_mtime:
                    continue
                
                with open(filepath) as f:
                    prompt_data = json.load(f)
                    prompt = Prompt(
                        name=prompt_data["name"],
                        template=prompt_data["template"],
                        input_variables=prompt_data["input_variables"],
                    )
                    self.prompts[prompt.name] = prompt
                    self._file_mtimes[filename] = current_mtime

    def get_prompt(self, name: str | list[str]) -> Prompt | None:
        """
        Gets a prompt by name. If a list of names is provided, the prompts are concatenated.
        """
        if isinstance(name, list):
            prompts_to_concat = [self.prompts.get(n) for n in name]
            valid_prompts = [p for p in prompts_to_concat if p]
            if not valid_prompts:
                return None

            concatenated_template = "".join([p.template for p in valid_prompts])
            all_input_variables: list[str] = []
            for p in valid_prompts:
                all_input_variables.extend(p.input_variables)

            return Prompt(
                name="concatenated_prompt",
                template=concatenated_template,
                input_variables=list(set(all_input_variables)),
            )

        return self.prompts.get(name)
