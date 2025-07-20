from __future__ import annotations

import json

from langchain_core.language_models import BaseChatModel

from talos.core.agent import Agent
from talos.hypervisor.supervisor import Supervisor
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager


class Hypervisor(Agent, Supervisor):
    """
    A class to monitor the agent's actions.
    """

    def __init__(self, llm: BaseChatModel, prompts_dir: str):
        super().__init__(
            model=llm,
            prompt_manager=FilePromptManager(prompts_dir),
            tool_manager=None,
        )

    def approve(self, messages: list, action: str, args: dict) -> bool:
        """
        Approves or denies an action.
        """
        prompt = self.prompt_manager.get_prompt("hypervisor")
        if not prompt:
            raise ValueError("Hypervisor prompt not found.")
        response = self.run(
            prompt.format(
                messages=messages,
                action=action,
                args=args,
            )
        )
        return json.loads(str(response))["approve"]
