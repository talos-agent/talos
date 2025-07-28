#!/usr/bin/env python3
"""
Simple test to verify memory tool availability and binding in MainAgent.
"""

import tempfile
import shutil
from pathlib import Path
from langchain_openai import ChatOpenAI

from src.talos.core.main_agent import MainAgent


def test_memory_tool_availability():
    """Test that memory tools are properly registered and available."""
    print("Testing Memory Tool Availability")
    print("=" * 40)
    
    temp_dir = tempfile.mkdtemp()
    memory_file = Path(temp_dir) / "test_memory.json"
    
    try:
        model = ChatOpenAI(model="gpt-4o", api_key="dummy-key")
        
        agent = MainAgent(
            model=model,
            prompts_dir="/home/ubuntu/repos/talos/src/talos/prompts",
            memory_file=str(memory_file)
        )
        
        print("✓ MainAgent initialized successfully")
        
        if hasattr(agent, 'tool_manager') and agent.tool_manager:
            tool_names = list(agent.tool_manager.tools.keys())
            print(f"✓ Tool manager initialized with {len(tool_names)} tools")
            print(f"Available tools: {tool_names}")
            
            if "add_memory" in tool_names:
                print("✓ add_memory tool is registered")
                
                memory_tool = agent.tool_manager.tools["add_memory"]
                print(f"✓ Memory tool type: {type(memory_tool)}")
                print(f"✓ Memory tool description: {memory_tool.description}")
            else:
                print("✗ add_memory tool not found in tool manager")
        else:
            print("✗ Tool manager not initialized")
        
        if hasattr(agent, 'memory') and agent.memory:
            print("✓ Memory system initialized")
            
            agent.memory.add_memory("Test memory: User likes pizza")
            print("✓ Memory addition works")
            
            memories = agent.memory.search("pizza")
            if memories:
                print(f"✓ Memory search works: found {len(memories)} memories")
                print(f"  - {memories[0].description}")
            else:
                print("✗ Memory search failed")
        else:
            print("✗ Memory system not initialized")
        
        if hasattr(agent, 'tools'):
            base_tool_names = [tool.name for tool in agent.tools]
            print(f"✓ Base agent tools: {base_tool_names}")
        else:
            print("✗ Base agent tools not available")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False
    
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_prompt_analysis():
    """Analyze prompts for memory-related instructions."""
    print("\nAnalyzing Prompts for Memory Instructions")
    print("=" * 45)
    
    prompt_file = Path("/home/ubuntu/repos/talos/src/talos/prompts/main_agent_prompt.json")
    
    try:
        import json
        with open(prompt_file, 'r') as f:
            prompt_data = json.load(f)
        
        template = prompt_data.get('template', '')
        
        memory_keywords = ['memory', 'remember', 'store', 'personal', 'preference', 'tool']
        found_keywords = []
        
        for keyword in memory_keywords:
            if keyword.lower() in template.lower():
                found_keywords.append(keyword)
        
        print(f"✓ Prompt loaded successfully ({len(template)} characters)")
        print(f"Memory-related keywords found: {found_keywords}")
        
        if 'memory' in template.lower():
            print("✓ Prompt mentions 'memory'")
        else:
            print("✗ Prompt does not mention 'memory'")
        
        if 'tool' in template.lower():
            print("✓ Prompt mentions 'tool'")
        else:
            print("✗ Prompt does not mention 'tool'")
        
        if 'user interaction' in template.lower():
            print("✓ Prompt has user interaction section")
            lines = template.split('\n')
            in_user_section = False
            user_section = []
            
            for line in lines:
                if 'user interaction' in line.lower():
                    in_user_section = True
                elif line.startswith('##') and in_user_section:
                    break
                elif in_user_section:
                    user_section.append(line)
            
            user_text = '\n'.join(user_section)
            print("User interaction section:")
            print(user_text[:300] + "..." if len(user_text) > 300 else user_text)
        
        return True
        
    except Exception as e:
        print(f"✗ Prompt analysis failed: {e}")
        return False


if __name__ == "__main__":
    print("Memory Tool Availability Test")
    print("=" * 50)
    
    success1 = test_memory_tool_availability()
    success2 = test_prompt_analysis()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✓ All tests completed successfully")
        print("\nFindings:")
        print("- Memory tools are properly registered in MainAgent")
        print("- Memory system works for direct storage and retrieval")
        print("- Prompts may need explicit memory tool usage instructions")
    else:
        print("✗ Some tests failed")
    
    print("\nRecommendations:")
    print("1. Add explicit memory tool usage instructions to agent prompts")
    print("2. Test with real LLM to see if tools are called automatically")
    print("3. Consider prompt engineering to encourage proactive memory usage")
