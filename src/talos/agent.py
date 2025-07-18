from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import Type

class Agent:
    def __init__(self, model: str, prompt_template: str, schema: Type[BaseModel]):
        self.model = ChatOpenAI(model=model)
        self.prompt_template = ChatPromptTemplate.from_template(prompt_template)
        self.schema = schema

    def run(self, **kwargs) -> BaseModel:
        structured_llm = self.model.with_structured_output(self.schema)
        chain = self.prompt_template | structured_llm
        result = chain.invoke(kwargs)
        if isinstance(result, BaseModel):
            return result
        else:
            raise TypeError(f"Expected a Pydantic model, but got {type(result)}")
