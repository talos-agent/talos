from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field, PrivateAttr
from typing import Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import BaseTool


class Agent(BaseModel):
    """
    Agent is a class that represents an agent that can interact with the user.

    Args:
        model_name: The name of the model to use.
        prompt_template: The prompt template to use.
        schema_class: The schema class to use for structured output.
        tools: A list of tools to use.
    """
    model_name: str = Field(..., alias="model")
    prompt_template: str = Field("You are a helpful assistant.\n{messages}", alias="prompt")
    schema_class: type[BaseModel] | None = Field(None, alias="schema")
    tools: list[type[BaseTool]] | None = None

    _prompt_template: ChatPromptTemplate = PrivateAttr()
    model: Any = None
    history: list[BaseMessage] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.model = ChatOpenAI(model=self.model_name)
        if self.tools:
            self.model = self.model.bind_tools(self.tools)
        self._prompt_template = ChatPromptTemplate.from_template(self.prompt_template)

    def run(self, message: str, history: list[BaseMessage] | None = None, **kwargs) -> BaseModel:
        if history:
            self.history.extend(history)

        self.history.append(HumanMessage(content=message))

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
