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
        from talos.utils.validation import sanitize_user_input
        
        if not self.prompt_manager:
            raise ValueError("Prompt manager not initialized.")
        
        if not action or not action.strip():
            raise ValueError("Action cannot be empty")
        
        action = sanitize_user_input(action, max_length=1000)
        
        if not isinstance(args, dict):
            raise ValueError("Args must be a dictionary")
        
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
        
        try:
            result = json.loads(str(response))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from hypervisor: {e}")
        
        if not isinstance(result, dict):
            raise ValueError("Hypervisor response must be a JSON object")
        
        if result.get("approve"):
            return True, None
        return False, result.get("reason")
