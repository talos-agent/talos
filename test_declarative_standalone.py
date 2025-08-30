#!/usr/bin/env python3
"""
Standalone test for the new declarative prompt configuration system.
This avoids circular import issues in the main test suite.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from talos.prompts.prompt_config import (
    PromptConfig, 
    StaticPromptSelector, 
    ConditionalPromptSelector
)
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
import tempfile
import json


def test_static_prompt_selector():
    """Test static prompt selector (backward compatibility)."""
    print("Testing StaticPromptSelector...")
    selector = StaticPromptSelector(prompt_names=["test_prompt"])
    result = selector.select_prompts({})
    assert result == ["test_prompt"], f"Expected ['test_prompt'], got {result}"
    print("✓ StaticPromptSelector works correctly")


def test_conditional_prompt_selector():
    """Test conditional prompt selector."""
    print("Testing ConditionalPromptSelector...")
    selector = ConditionalPromptSelector(
        conditions={"has_voice": "voice_prompt"},
        default_prompt="default_prompt"
    )
    
    result = selector.select_prompts({"has_voice": True})
    assert result == ["voice_prompt"], f"Expected ['voice_prompt'], got {result}"
    
    result = selector.select_prompts({})
    assert result == ["default_prompt"], f"Expected ['default_prompt'], got {result}"
    print("✓ ConditionalPromptSelector works correctly")


def test_prompt_config():
    """Test PromptConfig functionality."""
    print("Testing PromptConfig...")
    config = PromptConfig(
        selector=StaticPromptSelector(prompt_names=["test_prompt"]),
        variables={"test_var": "test_value"}
    )
    
    result = config.get_prompt_names({})
    assert result == ["test_prompt"], f"Expected ['test_prompt'], got {result}"
    print("✓ PromptConfig works correctly")


def test_file_prompt_manager_with_config():
    """Test FilePromptManager with declarative configuration."""
    print("Testing FilePromptManager with PromptConfig...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        prompt_file = os.path.join(temp_dir, "test_prompt.json")
        with open(prompt_file, 'w') as f:
            json.dump({
                "name": "test_prompt",
                "description": "Test prompt",
                "template": "Hello {name}, mode: {mode}!",
                "input_variables": ["name", "mode"]
            }, f)
        
        manager = FilePromptManager(prompts_dir=temp_dir)
        
        config = PromptConfig(
            selector=StaticPromptSelector(prompt_names=["test_prompt"]),
            variables={"name": "world", "mode": "test"},
            transformations={"mode": "uppercase"}
        )
        
        context = {}
        result = manager.get_prompt_with_config(config, context)
        
        assert result is not None, "Expected prompt result, got None"
        assert "Hello world, mode: TEST!" in result.template, f"Expected transformed template, got {result.template}"
        print("✓ FilePromptManager with PromptConfig works correctly")


def test_variable_transformations():
    """Test variable transformations."""
    print("Testing variable transformations...")
    
    from talos.prompts.prompt_manager import PromptManager
    
    class DummyManager(PromptManager):
        def get_prompt(self, name): pass
        def get_prompt_with_config(self, config, context): pass
    
    manager = DummyManager()
    
    template = "Hello {name}, mode: {mode}!"
    variables = {"name": "world", "mode": "test"}
    transformations = {"mode": "uppercase"}
    
    result = manager.apply_variable_transformations(template, variables, transformations)
    expected = "Hello world, mode: TEST!"
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✓ Variable transformations work correctly")


def main():
    """Run all tests."""
    print("=== Testing Declarative Prompt Configuration System ===\n")
    
    try:
        test_static_prompt_selector()
        test_conditional_prompt_selector()
        test_prompt_config()
        test_file_prompt_manager_with_config()
        test_variable_transformations()
        
        print("\n🎉 All tests passed! The declarative prompt system is working correctly.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
