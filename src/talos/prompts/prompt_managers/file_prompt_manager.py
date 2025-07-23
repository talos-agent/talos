import json
import os

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager


class FilePromptManager(PromptManager):
    """
    A class to manage prompts from files.
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
