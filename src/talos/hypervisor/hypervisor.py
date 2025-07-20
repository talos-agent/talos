from __future__ import annotations

import json
from typing import Any

from talos.core.agent import Agent
from talos.hypervisor.supervisor import Supervisor
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.tools.tool_manager import ToolManager


class Hypervisor(Agent, Supervisor):
    """
    A class to monitor the agent's actions.
    """

    prompts_dir: str
    agent: Agent | None = None

    def model_post_init(self, __context: Any) -> None:
        self.prompt_manager = FilePromptManager(self.prompts_dir)
        self.tool_manager = ToolManager()

    def set_agent(self, agent: Agent):
        """
        Sets the agent to be supervised.
        """
        self.agent = agent

    def approve(self, messages: list, action: str, args: dict) -> bool:
        """
        Approves or denies an action.
        """
        agent_history = self.agent.history if self.agent else []
        prompt = self.prompt_manager.get_prompt("hypervisor")
        if not prompt:
            raise ValueError("Hypervisor prompt not found.")
        response = self.run(
            prompt.format(
                messages=messages,
                action=action,
                args=args,
                agent_history=agent_history,
            )
        )
        return json.loads(str(response))["approve"]
