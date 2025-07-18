import os
from unittest.mock import patch
from pydantic import BaseModel, Field

os.environ["OPENAI_API_KEY"] = "test"
from talos.agent import Agent

class TestSchema(BaseModel):
    name: str = Field(description="The name of the person")
    age: int = Field(description="The age of the person")

@patch('src.talos.agent.ChatOpenAI')
class TestAgent:
    def test_agent(self, mock_chat_openai):
        # Configure the mock
        mock_instance = mock_chat_openai.return_value
        mock_instance.with_structured_output.return_value.invoke.return_value = TestSchema(name="John", age=30)

        # Create an instance of the Agent class
        agent = Agent(
            model="gpt-3.5-turbo",
            prompt_template="Generate a person with the name {name}.",
            schema=TestSchema,
        )

        # Run the agent
        response = agent.run(name="John")

        # Assert the response is as expected
        assert isinstance(response, TestSchema)
        assert response.name == "John"
        assert response.age == 30
