import pytest
from unittest.mock import MagicMock
from langchain_core.language_models import BaseChatModel
from talos.agent import Agent
from talos.prompts.prompt_manager import PromptManager
from langchain_core.messages import HumanMessage, AIMessage

from talos.prompts.prompt import Prompt

class MockPromptManager(PromptManager):
    def get_prompt(self, name: str) -> Prompt | None:
        return Prompt(name="default", template="test template", input_variables=[])

@pytest.fixture
def prompt_manager():
    return MockPromptManager()

class MockChatModel(BaseChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        return MagicMock()

    def _llm_type(self):
        return "mock"


def test_reset_history(prompt_manager):
    agent = Agent(model=MockChatModel(), prompt_manager=prompt_manager)
    agent.add_to_history([HumanMessage(content="hello")])
    assert len(agent.history) == 1
    agent.reset_history()
    assert len(agent.history) == 0

def test_add_to_history(prompt_manager):
    agent = Agent(model=MockChatModel(), prompt_manager=prompt_manager)
    messages = [
        HumanMessage(content="hello"),
        AIMessage(content="hi there"),
    ]
    agent.add_to_history(messages)
    assert len(agent.history) == 2
    assert agent.history[0].content == "hello"
    assert agent.history[1].content == "hi there"
