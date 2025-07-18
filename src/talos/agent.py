from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from typing import Type, List, Optional, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

class Agent(BaseModel):
    model_name: str = Field(..., alias="model")
    prompt_template_str: str = Field(..., alias="prompt_template")
    schema_class: Type[BaseModel] = Field(..., alias="schema")
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

        structured_llm = self.model.with_structured_output(self.schema)
        chain = self.prompt_template | structured_llm

        # Pass the history to the chain
        result = chain.invoke({"messages": self.history})

        if isinstance(result, BaseModel):
            self.history.append(AIMessage(content=str(result)))
            return result
        else:
            raise TypeError(f"Expected a Pydantic model, but got {type(result)}")
