import os
import json
from talos.prompts.prompt import Prompt


class PromptManager:
    """
    A class to manage prompts.
    """

    def __init__(self, prompts_dir: str):
        self.prompts_dir = prompts_dir
        self.prompts: dict[str, Prompt] = {}
        self.load_prompts()

    def load_prompts(self) -> None:
        """
        Loads all prompts from the prompts directory.
        """
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.prompts_dir, filename)) as f:
                    prompt_data = json.load(f)
                    prompt = Prompt(
                        name=prompt_data["name"],
                        template=prompt_data["template"],
                        input_variables=prompt_data["input_variables"],
                    )
                    self.prompts[prompt.name] = prompt

    def get_prompt(self, name: str) -> Prompt:
        """
        Gets a prompt by name.
        """
        return self.prompts.get(name)
