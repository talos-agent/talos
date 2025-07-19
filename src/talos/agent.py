from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, PrivateAttr
from typing import Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from talos.tools.tool_manager import ToolManager
from talos.prompts.prompt_manager import PromptManager


from pydantic import ConfigDict

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
    model_name: str = Field(..., alias="model")
    prompt_manager: PromptManager = Field(..., alias="prompt_manager")
    schema_class: type[BaseModel] | None = Field(None, alias="schema")
    tool_manager: ToolManager = Field(default_factory=ToolManager, alias="tool_manager")

    _prompt_template: ChatPromptTemplate = PrivateAttr()
    model: Any = None
    history: list[BaseMessage] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.model = None
        self.set_prompt()

    def set_prompt(self, name: str = "default"):
        prompt = self.prompt_manager.get_prompt(name)
        if not prompt:
            raise ValueError(f"The prompt '{name}' is not defined.")
        self._prompt_template = ChatPromptTemplate.from_template(prompt.template)

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

    def _add_context(self, query: str, **kwargs) -> str:
        """
        A base method for adding context to the query.
        """
        return query

    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:
        if not self.model:
            self.model = ChatOpenAI(model=self.model_name)
        if history:
            self.history.extend(history)

        message_with_context = self._add_context(message, **kwargs)
        self.history.append(HumanMessage(content=message_with_context))

        tools = self.tool_manager.get_all_tools()
        if tools:
            self.model = self.model.bind_tools(tools)

        if self.schema_class:
            structured_llm = self.model.with_structured_output(self.schema_class)
            chain = self._prompt_template | structured_llm
        else:
            chain = self._prompt_template | self.model

        # Pass the history to the chain
        result = chain.invoke({"messages": self.history, **kwargs})

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
