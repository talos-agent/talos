import pytest
from unittest.mock import MagicMock, patch

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_config import (
    PromptConfig, 
    StaticPromptSelector, 
    ConditionalPromptSelector
)
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.dag.nodes import PromptNode, GraphState

PromptNode.model_rebuild()


def test_static_prompt_selector():
    """Test static prompt selector (backward compatibility)."""
    selector = StaticPromptSelector(prompt_names=["test_prompt"])
    result = selector.select_prompts({})
    assert result == ["test_prompt"]


def test_conditional_prompt_selector():
    """Test conditional prompt selector."""
    selector = ConditionalPromptSelector(
        conditions={"has_voice": "voice_prompt"},
        default_prompt="default_prompt"
    )
    
    result = selector.select_prompts({"has_voice": True})
    assert result == ["voice_prompt"]
    
    result = selector.select_prompts({})
    assert result == ["default_prompt"]


def test_prompt_config_integration():
    """Test PromptConfig with PromptNode."""
    config = PromptConfig(
        selector=StaticPromptSelector(prompt_names=["test_prompt"]),
        variables={"test_var": "test_value"}
    )
    
    mock_manager = MagicMock(spec=FilePromptManager)
    mock_manager.get_prompt_with_config.return_value = Prompt(
        name="test", template="Test template", input_variables=[]
    )
    
    node = PromptNode(
        node_id="test_node",
        name="Test Node",
        prompt_manager=mock_manager,
        prompt_config=config
    )
    
    state: GraphState = {
        "messages": [],
        "context": {},
        "current_query": "test",
        "results": {},
        "metadata": {}
    }
    
    result = node.execute(state)
    assert "Applied prompt using declarative config" in result["results"]["test_node"]


def test_prompt_node_validation():
    """Test that PromptNode requires either prompt_names or prompt_config."""
    mock_manager = MagicMock()
    
    with pytest.raises(ValueError, match="Either prompt_names or prompt_config must be provided"):
        PromptNode(
            node_id="test_node",
            name="Test Node",
            prompt_manager=mock_manager
        )


def test_file_prompt_manager_with_config():
    """Test FilePromptManager with declarative config."""
    with patch("os.listdir", return_value=[]):
        manager = FilePromptManager(prompts_dir="dummy_dir")
    
    manager.prompts = {
        "test_prompt": Prompt(
            name="test_prompt",
            template="Hello {name}!",
            input_variables=["name"]
        )
    }
    
    config = PromptConfig(
        selector=StaticPromptSelector(prompt_names=["test_prompt"]),
        variables={"name": "world"}
    )
    
    result = manager.get_prompt_with_config(config, {})
    assert result is not None
    assert "Hello world!" in result.template


def test_variable_transformations():
    """Test variable transformations in prompt manager."""
    with patch("os.listdir", return_value=[]):
        manager = FilePromptManager(prompts_dir="dummy_dir")
    
    template = "Mode: {mode}"
    variables = {"mode": "test"}
    transformations = {"mode": "uppercase"}
    
    result = manager.apply_variable_transformations(template, variables, transformations)
    assert result == "Mode: TEST"
