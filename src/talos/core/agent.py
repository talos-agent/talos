from __future__ import annotations

from typing import Any, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from talos.core.memory import Memory
from talos.data.dataset_manager import DatasetManager
from talos.hypervisor.supervisor import Supervisor
from talos.prompts.prompt_manager import PromptManager
from talos.tools.memory_tool import AddMemoryTool
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
        user_id: Optional user identifier for conversation tracking.
        session_id: Optional session identifier for conversation grouping.
        use_database_memory: Whether to use database-backed memory instead of files.
    """

    model: BaseChatModel | Runnable
    prompt_manager: PromptManager | None = Field(None, alias="prompt_manager")
    schema_class: type[BaseModel] | None = Field(None, alias="schema")
    tool_manager: ToolManager = Field(default_factory=ToolManager, alias="tool_manager")
    supervisor: Optional[Supervisor] = None
    is_main_agent: bool = False
    memory: Optional[Memory] = None
    dataset_manager: Optional[DatasetManager] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    use_database_memory: bool = False

    _prompt_template: ChatPromptTemplate = PrivateAttr()
    history: list[BaseMessage] = []

    def model_post_init(self, __context: Any) -> None:
        if self.memory:
            self.tool_manager.register_tool(AddMemoryTool(agent=self))

    def set_prompt(self, name: str | list[str]):
        if not self.prompt_manager:
            raise ValueError("Prompt manager not initialized.")
        
        prompt_names = name if isinstance(name, list) else [name]
        if self.dataset_manager:
            prompt_names.append("relevant_documents_prompt")
        
        prompt = self.prompt_manager.get_prompt(prompt_names)
        if not prompt:
            raise ValueError(f"The prompt '{prompt_names}' is not defined.")
        # Build a chat prompt that contains the system template and leaves a
        # placeholder for the ongoing conversation (`messages`).
        # This allows the user input and prior history to be provided to the
        # model at runtime so that responses can be contextual and not ignore
        # the latest message.
        self._prompt_template = ChatPromptTemplate.from_messages(
            [
                ("system", prompt.template),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

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
        context = {}
        
        if self.dataset_manager:
            relevant_documents = self.dataset_manager.search(query, k=5)
            context["relevant_documents"] = relevant_documents
            
        return context

    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:
        if self.memory:
            relevant_memories = self.memory.search(message)
            kwargs["relevant_memories"] = relevant_memories
        self._prepare_run(message, history)
        chain = self._create_chain()
        context = self._build_context(message, **kwargs)
        result = chain.invoke({"messages": self.history, **context, **kwargs})
        processed_result = self._process_result(result)
        if self.memory:
            self.memory.save_history(self.history)
        return processed_result

    def add_memory(self, description: str, metadata: Optional[dict] = None):
        if self.memory:
            self.memory.add_memory(description, metadata)

    def _prepare_run(self, message: str, history: list[BaseMessage] | None = None) -> None:
        if history:
            self.history.clear()
            self.history.extend(history)
        if self.prompt_manager:
            self.prompt_manager.update_prompt_template(self.history)
        self.history.append(HumanMessage(content=message))
        tools = self.tool_manager.get_all_tools()
        for tool in tools:
            if isinstance(tool, SupervisedTool):
                tool.set_supervisor(self.supervisor)
        if tools and isinstance(self.model, BaseChatModel):
            self.model = self.model.bind_tools(tools)

    def _create_chain(self) -> Runnable:
        if self.schema_class and isinstance(self.model, BaseChatModel):
            structured_llm = self.model.with_structured_output(self.schema_class)
            return self._prompt_template | structured_llm
        return self._prompt_template | self.model

    def _process_result(self, result: Any) -> BaseModel:
        if isinstance(result, BaseModel):
            self.history.append(AIMessage(content=str(result)))
            return result
        if isinstance(result, dict) and self.schema_class:
            modelled_result = self.schema_class.parse_obj(result)
            self.history.append(AIMessage(content=str(modelled_result)))
            return modelled_result
        if isinstance(result, AIMessage):
            self.history.append(result)
            return result
        raise TypeError(f"Expected a Pydantic model or a dictionary, but got {type(result)}")
