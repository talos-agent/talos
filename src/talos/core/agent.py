from __future__ import annotations

from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from talos.hypervisor.supervisor import Supervisor
from talos.prompts.prompt_manager import PromptManager
from talos.tools.supervised_tool import SupervisedTool
from talos.tools.tool_manager import ToolManager


class Agent(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """
    Agent is a class that represents an agent that can interact with the user.

    Args:
        model_name: The name of the model to use.
        prompt_manager: The prompt manager to use.
        schema_class: The schema class to use for structured output.
        tool_manager: The tool manager to use.
    """
    model: BaseChatModel
    prompt_manager: PromptManager = Field(..., alias="prompt_manager")
    schema_class: type[BaseModel] | None = Field(None, alias="schema")
    tool_manager: ToolManager = Field(default_factory=ToolManager, alias="tool_manager")
    supervisor: Optional[Supervisor] = None
    is_main_agent: bool = False

    _prompt_template: ChatPromptTemplate = PrivateAttr()
    history: list[BaseMessage] = []

    def set_prompt(self, name: str):
        prompt = self.prompt_manager.get_prompt(name)
        if not prompt:
            raise ValueError(f"The prompt '{name}' is not defined.")
        self._prompt_template = ChatPromptTemplate.from_template(prompt.template)

    def add_supervisor(self, supervisor: Supervisor):
        """
        Adds a supervisor to the agent.
        """
        self.supervisor = supervisor

    def add_to_history(self, messages: list[BaseMessage]):
        """
        Adds a list of messages to the history.
        """
        self.history.extend(messages)

    def reset_history(self):
        """
        Resets the history of the agent.
        """
        self.history = []

    def _build_context(self, query: str, **kwargs) -> dict:
        """
        A base method for adding context to the query.
        """
        return {}

    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:
        if history:
            self.history.extend(history)

        self.prompt_manager.update_prompt_template(self.history)

        self.history.append(HumanMessage(content=message))

        tools = self.tool_manager.get_all_tools()
        for tool in tools:
            if isinstance(tool, SupervisedTool):
                tool.set_supervisor(self.supervisor)

        if tools:
            self.model = self.model.bind_tools(tools)  # type: ignore

        if self.schema_class:
            structured_llm = self.model.with_structured_output(self.schema_class)
            chain = self._prompt_template | structured_llm
        else:
            chain = self._prompt_template | self.model

        # Pass the history to the chain
        context = self._build_context(message, **kwargs)
        result = chain.invoke({"messages": self.history, **context, **kwargs})

        if isinstance(result, BaseModel):
            self.history.append(AIMessage(content=str(result)))
            return result
        elif isinstance(result, dict) and self.schema_class:
            modelled_result = self.schema_class.parse_obj(result)
            self.history.append(AIMessage(content=str(modelled_result)))
            return modelled_result
        elif isinstance(result, AIMessage):
            self.history.append(result)
            return result
        else:
            raise TypeError(f"Expected a Pydantic model or a dictionary, but got {type(result)}")
