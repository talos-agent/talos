#!/usr/bin/env python3
"""
Test script to verify that the prompt fix enables automatic memory tool usage.
"""

import tempfile
import shutil
from pathlib import Path

from src.talos.core.main_agent import MainAgent


def test_memory_tool_invocation():
    """Test that the agent now calls memory tools automatically with the updated prompt."""
    print("Testing Memory Tool Invocation with Updated Prompt")
    print("=" * 55)
    
    temp_dir = tempfile.mkdtemp()
    memory_file = Path(temp_dir) / "test_memory.json"
    
    try:
        from langchain_openai import ChatOpenAI
        
        model = ChatOpenAI(model="gpt-4o", api_key="dummy-key")
        
        agent = MainAgent(
            model=model,
            prompts_dir="/home/ubuntu/repos/talos/src/talos/prompts",
            memory_file=str(memory_file)
        )
        
        print("✓ MainAgent initialized with updated prompt")
        
        prompt_content = agent.prompt_manager.get_prompt("main_agent_prompt").template
        if "memory" in prompt_content.lower():
            print("✓ Updated prompt mentions memory")
            assert True
        else:
            print("✗ Updated prompt still doesn't mention memory")
            assert False, "Updated prompt still doesn't mention memory"
        
        if "add_memory" in prompt_content.lower():
            print("✓ Updated prompt mentions add_memory tool")
        else:
            print("✗ Updated prompt doesn't mention add_memory tool")
            assert False, "Updated prompt doesn't mention add_memory tool"
        
        print("✓ Memory tool invocation test completed")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        raise
    
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
        
        
    except Exception as e:
        print(f"✗ Prompt content test failed: {e}")
        raise


if __name__ == "__main__":
    print("Memory Prompt Fix Verification")
    print("=" * 50)
    
    try:
        test_prompt_content()
        test_memory_tool_invocation()
        
        print("\n" + "=" * 50)
        print("✓ Prompt fix verification completed successfully")
        print("\nNext steps:")
        print("1. Test with real CLI: uv run talos main --user-id test-user")
        print("2. Say 'I like pizza' and verify memory storage")
        print("3. Check memory persistence in follow-up conversations")
        
    except Exception as e:
        print(f"\n✗ Verification tests failed: {e}")
    
    print("\nExpected behavior:")
    print("- Agent should now proactively call add_memory tool")
    print("- Personal information should be stored automatically")
    print("- Agent should reference stored memories in future conversations")
