from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Type, List, Optional, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class Agent(BaseModel):
    model_name: str = Field(..., alias="model")
    prompt_template_str: str = Field(..., alias="prompt_template")
    schema_class: Optional[Type[BaseModel]] = Field(None, alias="schema")
    tools: Optional[List] = None

    model: Any = None
    prompt_template: Any = None
    history: List[BaseMessage] = []

    def __init__(self, **data):
        super().__init__(**data)
        self.model = ChatOpenAI(model=self.model_name)
        if self.tools:
            self.model = self.model.bind_tools(self.tools)
        self.prompt_template = ChatPromptTemplate.from_template(self.prompt_template_str)

    def run(self, message: str, history: Optional[List[BaseMessage]] = None) -> BaseModel:
        if history:
            self.history.extend(history)

        self.history.append(HumanMessage(content=message))

        if self.schema_class:
            structured_llm = self.model.with_structured_output(self.schema_class)
            chain = self.prompt_template | structured_llm
        else:
            chain = self.prompt_template | self.model

        # Pass the history to the chain
        result = chain.invoke({"messages": self.history})

        if isinstance(result, BaseModel):
            self.history.append(AIMessage(content=str(result)))
            return result
        elif isinstance(result, dict) and self.schema_class:
            modelled_result = self.schema_class.parse_obj(result)
            self.history.append(AIMessage(content=str(modelled_result)))
            return modelled_result
        elif isinstance(result, AIMessage):
             self.history.append(result)
             return result.content
        else:
            raise TypeError(f"Expected a Pydantic model or a dictionary, but got {type(result)}")
