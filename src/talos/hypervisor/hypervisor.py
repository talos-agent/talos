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

    def register_agent(self, agent: Agent):
        """
        Registers an agent with the hypervisor.
        """
        self.agent = agent

    def approve(self, action: str, args: dict) -> tuple[bool, str | None]:
        """
        Approves or denies an action.
        """
        if not self.prompt_manager:
            raise ValueError("Prompt manager not initialized.")
        agent_history = self.agent.history if self.agent else []
        prompt = self.prompt_manager.get_prompt("hypervisor")
        if not prompt:
            raise ValueError("Hypervisor prompt not found.")
        response = self.run(
            prompt.format(
                messages=agent_history,
                action=action,
                args=args,
                agent_history=agent_history,
            )
        )
        result = json.loads(str(response))
        if result["approve"]:
            return True, None
        return False, result.get("reason")
