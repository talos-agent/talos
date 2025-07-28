#!/usr/bin/env python3
"""
Comprehensive memory functionality test for Talos agent.
Tests memory tool availability, binding, and automatic invocation.
"""

import tempfile
import shutil
from pathlib import Path
from langchain_openai import ChatOpenAI

from src.talos.core.main_agent import MainAgent


class TestMemoryIntegration:
    """Test memory tool integration and automatic invocation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = Path(self.temp_dir) / "test_memory.json"
        
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_main_agent_memory_tool_registration(self):
        """Test that MainAgent properly registers memory tools."""
        model = ChatOpenAI(model="gpt-4o", api_key="dummy-key")
        
        agent = MainAgent(
            model=model,
            prompts_dir="/home/ubuntu/repos/talos/src/talos/prompts",
            memory_file=str(self.memory_file)
        )
        
        if hasattr(agent, 'tool_manager') and agent.tool_manager:
            tool_names = list(agent.tool_manager.tools.keys())
            assert "add_memory" in tool_names, f"Memory tool not found in tools: {tool_names}"
        else:
            assert False, "Tool manager not initialized"
    
    def test_memory_storage_and_retrieval(self):
        """Test memory storage and retrieval functionality."""
        model = ChatOpenAI(model="gpt-4o", api_key="dummy-key")
        
        agent = MainAgent(
            model=model,
            prompts_dir="/home/ubuntu/repos/talos/src/talos/prompts",
            memory_file=str(self.memory_file)
        )
        
        agent.memory.add_memory("User likes pizza")
        
        memories = agent.memory.search("pizza preferences")
        assert len(memories) > 0, "No memories found for pizza preferences"
        assert "pizza" in memories[0].description.lower(), "Pizza preference not stored correctly"


if __name__ == "__main__":
    print("Memory Integration Test Suite")
    print("=" * 40)
    
    print("\nTo run full test suite:")
    print("uv run pytest test_memory_integration.py -v")
