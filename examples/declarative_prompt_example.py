"""
Example demonstrating the new declarative prompt configuration system.
"""

from talos.prompts.prompt_config import (
    PromptConfig, 
    StaticPromptSelector, 
    ConditionalPromptSelector
)
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager


def example_static_configuration():
    """Example of static prompt configuration (backward compatibility)."""
    config = PromptConfig(
        selector=StaticPromptSelector(
            prompt_names=["main_agent_prompt", "general_agent_prompt"]
        )
    )
    
    print("Static configuration prompt names:", config.get_prompt_names({}))


def example_conditional_configuration():
    """Example of conditional prompt configuration."""
    config = PromptConfig(
        selector=ConditionalPromptSelector(
            conditions={
                "has_voice_analysis": "voice_enhanced_agent_prompt",
                "is_proposal_context": "proposal_evaluation_prompt",
                "is_github_context": "github_pr_review_prompt"
            },
            default_prompt="main_agent_prompt"
        ),
        variables={
            "system_mode": "autonomous",
            "safety_level": "high"
        },
        transformations={
            "system_mode": "uppercase"
        }
    )
    
    context_with_voice = {"has_voice_analysis": True}
    context_github = {"is_github_context": True}
    context_default = {}
    
    print("Voice context prompts:", config.get_prompt_names(context_with_voice))
    print("GitHub context prompts:", config.get_prompt_names(context_github))
    print("Default context prompts:", config.get_prompt_names(context_default))


def example_with_prompt_manager():
    """Example using the new system with a prompt manager."""
    import tempfile
    import os
    import json
    
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
        
        if result:
            print("Enhanced template:", result.template)
        else:
            print("Failed to get prompt")


if __name__ == "__main__":
    print("=== Declarative Prompt Configuration Examples ===\n")
    
    print("1. Static Configuration:")
    example_static_configuration()
    print()
    
    print("2. Conditional Configuration:")
    example_conditional_configuration()
    print()
    
    print("3. With Prompt Manager:")
    example_with_prompt_manager()
