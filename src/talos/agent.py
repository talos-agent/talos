from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel

class Agent:
    def __init__(self, model: str, prompt_template: str, schema: BaseModel):
        self.model = ChatOpenAI(model=model)
        self.prompt_template = ChatPromptTemplate.from_template(prompt_template)
        self.schema = schema

    def run(self, **kwargs) -> BaseModel:
        structured_llm = self.model.with_structured_output(self.schema)
        chain = self.prompt_template | structured_llm
        return chain.invoke(kwargs)
