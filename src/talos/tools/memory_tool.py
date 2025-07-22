from __future__ import annotations

from typing import TYPE_CHECKING, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from talos.core.agent import Agent


class AddMemorySchema(BaseModel):
    """Pydantic schema for adding a memory."""

    description: str = Field(..., description="The description of the memory to add.")


class AddMemoryTool(BaseTool):
    """Tool for adding a memory to the agent's memory."""

    name: str = "add_memory"
    description: str = "Adds a memory to the agent's memory."
    args_schema: Type[BaseModel] = AddMemorySchema
    agent: Agent

    def _run(self, description: str) -> str:
        """Adds a memory to the agent's memory."""
        self.agent.add_memory(description)
        return f"Memory added: {description}"
