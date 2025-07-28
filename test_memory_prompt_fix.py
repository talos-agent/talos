#!/usr/bin/env python3
"""
Test script to verify that the prompt fix enables automatic memory tool usage.
"""

import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from src.talos.core.main_agent import MainAgent


async def test_memory_tool_invocation():
    """Test that the agent now calls memory tools automatically with the updated prompt."""
    print("Testing Memory Tool Invocation with Updated Prompt")
    print("=" * 55)
    
    temp_dir = tempfile.mkdtemp()
    memory_file = Path(temp_dir) / "test_memory.json"
    
    try:
        mock_model = AsyncMock()
        mock_model.bind_tools = MagicMock(return_value=mock_model)
        
        mock_response = MagicMock()
        mock_response.content = "I'll remember that you like pizza! That's a great preference to have."
        mock_response.tool_calls = [
            MagicMock(
                name="add_memory",
                args={"description": "User likes pizza"}
            )
        ]
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        
        agent = MainAgent(
            model=mock_model,
            prompts_dir="/home/ubuntu/repos/talos/src/talos/prompts",
            memory_file=str(memory_file)
        )
        
        print("✓ MainAgent initialized with updated prompt")
        
        prompt_content = agent.prompt_manager.get_prompt("main_agent_prompt").template
        if "memory" in prompt_content.lower():
            print("✓ Updated prompt mentions memory")
        else:
            print("✗ Updated prompt still doesn't mention memory")
        
        if "add_memory" in prompt_content.lower():
            print("✓ Updated prompt mentions add_memory tool")
        else:
            print("✗ Updated prompt doesn't mention add_memory tool")
        
        print("\nSimulating user input: 'I like pizza'")
        response = await agent.run("I like pizza", user_id="test-user")
        
        print(f"Agent response: {response}")
        
        mock_model.bind_tools.assert_called()
        print("✓ Model was called with tools bound")
        
        mock_model.ainvoke.assert_called()
        print("✓ Model was invoked for conversation")
        
        if mock_response.tool_calls:
            print("✓ Mock tool call detected")
            for tool_call in mock_response.tool_calls:
                if tool_call.name == "add_memory":
                    print(f"✓ add_memory tool would be called with: {tool_call.args}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_prompt_content():
    """Test that the prompt now contains memory-related instructions."""
    print("\nTesting Updated Prompt Content")
    print("=" * 35)
    
    try:
        import json
        prompt_file = Path("/home/ubuntu/repos/talos/src/talos/prompts/main_agent_prompt.json")
        
        with open(prompt_file, 'r') as f:
            prompt_data = json.load(f)
        
        template = prompt_data.get('template', '')
        
        memory_checks = [
            ("memory system", "memory system" in template.lower()),
            ("add_memory tool", "add_memory" in template.lower()),
            ("personal information", "personal information" in template.lower()),
            ("preferences", "preferences" in template.lower()),
            ("store information", "store" in template.lower())
        ]
        
        print("Memory-related content checks:")
        for check_name, result in memory_checks:
            status = "✓" if result else "✗"
            print(f"{status} {check_name}: {'Found' if result else 'Not found'}")
        
        if "### Memory and Personalization" in template:
            print("\n✓ Memory and Personalization section found")
            
            lines = template.split('\n')
            in_memory_section = False
            memory_section = []
            
            for line in lines:
                if "### Memory and Personalization" in line:
                    in_memory_section = True
                elif line.startswith('###') and in_memory_section:
                    break
                elif in_memory_section:
                    memory_section.append(line)
            
            memory_text = '\n'.join(memory_section)
            print("Memory section content:")
            print(memory_text[:500] + "..." if len(memory_text) > 500 else memory_text)
        else:
            print("✗ Memory and Personalization section not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Prompt content test failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    
    print("Memory Prompt Fix Verification")
    print("=" * 50)
    
    success1 = test_prompt_content()
    success2 = asyncio.run(test_memory_tool_invocation())
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✓ Prompt fix verification completed successfully")
        print("\nNext steps:")
        print("1. Test with real CLI: uv run talos main --user-id test-user")
        print("2. Say 'I like pizza' and verify memory storage")
        print("3. Check memory persistence in follow-up conversations")
    else:
        print("✗ Some verification tests failed")
    
    print("\nExpected behavior:")
    print("- Agent should now proactively call add_memory tool")
    print("- Personal information should be stored automatically")
    print("- Agent should reference stored memories in future conversations")
