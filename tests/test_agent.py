import pytest
from langchain_core.messages import HumanMessage, AIMessage
from talos.agent import Agent
from unittest.mock import MagicMock
import talos.agent
from talos.prompts.prompt_manager import PromptManager

@pytest.fixture
def agent(monkeypatch, tmp_path):
    mock_chat_open_ai = MagicMock()
    monkeypatch.setattr(talos.agent, "ChatOpenAI", mock_chat_open_ai)
    prompts_dir = tmp_path / "prompts"
    prompts_dir.mkdir()
    return Agent(model="gpt-3.5-turbo", prompt_manager=PromptManager(str(prompts_dir)))

def test_reset_history(agent: Agent):
    agent.add_message_to_history(HumanMessage(content="Hello"))
    agent.add_message_to_history(AIMessage(content="Hi there!"))
    assert len(agent.history) == 2
    agent.reset_history()
    assert len(agent.history) == 0

def test_add_message_to_history(agent: Agent):
    assert len(agent.history) == 0
    agent.add_message_to_history(HumanMessage(content="Hello"))
    assert len(agent.history) == 1
    agent.add_message_to_history(AIMessage(content="Hi there!"))
    assert len(agent.history) == 2
    assert isinstance(agent.history[0], HumanMessage)
    assert isinstance(agent.history[1], AIMessage)
    assert agent.history[0].content == "Hello"
    assert agent.history[1].content == "Hi there!"
