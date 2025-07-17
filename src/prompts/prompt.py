from typing import List, Dict


class Prompt:
    """
    A class to represent a prompt.
    """

    def __init__(self, name: str, template: str, input_variables: List[str]):
        self.name = name
        self.template = template
        self.input_variables = input_variables

    def format(self, **kwargs) -> str:
        """
        Formats the prompt with the given arguments.
        """
        return self.template.format(**kwargs)
