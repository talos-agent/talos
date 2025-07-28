#!/usr/bin/env python3
"""
Comprehensive memory functionality test for Talos agent.
Tests memory tool availability, binding, and automatic invocation.
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

from src.talos.core.main_agent import MainAgent
from src.talos.core.agent import Agent
from src.talos.core.memory import Memory
from src.talos.tools.memory_tool import AddMemoryTool
from src.talos.prompts.prompt_manager import PromptManager


class TestMemoryIntegration:
    """Test memory tool integration and automatic invocation."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = Path(self.temp_dir) / "test_memory.json"
        
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_main_agent_memory_tool_registration(self):
        """Test that MainAgent properly registers memory tools."""
        with patch('src.talos.core.main_agent.get_model') as mock_get_model:
            mock_model = AsyncMock()
            mock_get_model.return_value = mock_model
            
            agent = MainAgent(
                model_name="gpt-4o",
                memory_file=str(self.memory_file),
                prompt_manager=PromptManager()
            )
            
            tool_names = [tool.name for tool in agent.tools]
            assert "add_memory" in tool_names, f"Memory tool not found in tools: {tool_names}"
    
    @pytest.mark.asyncio
    async def test_base_agent_memory_tool_registration(self):
        """Test that base Agent properly registers AddMemoryTool."""
        with patch('src.talos.core.agent.get_model') as mock_get_model:
            mock_model = AsyncMock()
            mock_get_model.return_value = mock_model
            
            memory = Memory(memory_file=str(self.memory_file))
            agent = Agent(
                model_name="gpt-4o",
                memory=memory,
                prompt_manager=PromptManager()
            )
            
            tool_names = [tool.name for tool in agent.tools]
            assert "add_memory" in tool_names, f"AddMemoryTool not found in tools: {tool_names}"
    
    @pytest.mark.asyncio
    async def test_memory_storage_and_retrieval(self):
        """Test memory storage and retrieval functionality."""
        with patch('src.talos.core.main_agent.get_model') as mock_get_model:
            mock_model = AsyncMock()
            mock_get_model.return_value = mock_model
            
            agent = MainAgent(
                model_name="gpt-4o",
                memory_file=str(self.memory_file),
                prompt_manager=PromptManager()
            )
            
            await agent.add_memory("User likes pizza", user_id="test-user")
            
            memories = agent.memory.search("pizza preferences", user_id="test-user")
            assert len(memories) > 0, "No memories found for pizza preferences"
            assert "pizza" in memories[0].description.lower(), "Pizza preference not stored correctly"
    
    @pytest.mark.asyncio
    async def test_tool_binding_during_conversation(self):
        """Test that memory tools are properly bound during conversations."""
        with patch('src.talos.core.main_agent.get_model') as mock_get_model:
            mock_model = AsyncMock()
            mock_model.bind_tools = MagicMock(return_value=mock_model)
            mock_get_model.return_value = mock_model
            
            agent = MainAgent(
                model_name="gpt-4o",
                memory_file=str(self.memory_file),
                prompt_manager=PromptManager()
            )
            
            await agent._prepare_run("test-user")
            
            mock_model.bind_tools.assert_called_once()
            bound_tools = mock_model.bind_tools.call_args[0][0]
            tool_names = [tool.name for tool in bound_tools]
            assert "add_memory" in tool_names, "Memory tool not bound to model"
    
    @pytest.mark.asyncio
    async def test_pizza_preference_scenario(self):
        """Test the specific 'I like pizza' scenario."""
        with patch('src.talos.core.main_agent.get_model') as mock_get_model:
            mock_model = AsyncMock()
            mock_model.bind_tools = MagicMock(return_value=mock_model)
            
            mock_response = MagicMock()
            mock_response.content = "I'll remember that you like pizza!"
            mock_response.tool_calls = [
                MagicMock(
                    name="add_memory",
                    args={"description": "User likes pizza"}
                )
            ]
            mock_model.ainvoke = AsyncMock(return_value=mock_response)
            mock_get_model.return_value = mock_model
            
            agent = MainAgent(
                model_name="gpt-4o",
                memory_file=str(self.memory_file),
                prompt_manager=PromptManager()
            )
            
            response = await agent.run("I like pizza", user_id="test-user")
            
            memories = agent.memory.search("pizza", user_id="test-user")
            assert len(memories) > 0, "Pizza preference not stored in memory"
            
            assert "pizza" in response.lower(), "Response doesn't acknowledge pizza preference"


class TestMemoryToolAvailability:
    """Test memory tool availability and functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = Path(self.temp_dir) / "test_memory.json"
        
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_memory_tool_functionality(self):
        """Test AddMemoryTool functionality directly."""
        agent = MagicMock()
        agent.add_memory = AsyncMock()
        
        tool = AddMemoryTool()
        
        asyncio.run(tool._run("User prefers Italian food", agent=agent))
        
        agent.add_memory.assert_called_once_with("User prefers Italian food")
    
    @pytest.mark.asyncio
    async def test_main_agent_custom_memory_tool(self):
        """Test MainAgent's custom _add_memory_tool implementation."""
        with patch('src.talos.core.main_agent.get_model') as mock_get_model:
            mock_model = AsyncMock()
            mock_get_model.return_value = mock_model
            
            agent = MainAgent(
                model_name="gpt-4o",
                memory_file=str(self.memory_file),
                prompt_manager=PromptManager()
            )
            
            memory_tool = None
            for tool in agent.tools:
                if tool.name == "add_memory":
                    memory_tool = tool
                    break
            
            assert memory_tool is not None, "Custom memory tool not found"
            
            await memory_tool.func("User enjoys spicy food")
            
            memories = agent.memory.search("spicy food")
            assert len(memories) > 0, "Spicy food preference not stored"


async def run_interactive_test():
    """Interactive test to verify memory functionality in CLI-like environment."""
    print("Running interactive memory test...")
    
    temp_dir = tempfile.mkdtemp()
    memory_file = Path(temp_dir) / "interactive_test_memory.json"
    
    try:
        mock_model = AsyncMock()
        mock_model.bind_tools = MagicMock(return_value=mock_model)
        
        agent = MainAgent(
            model=mock_model,
            prompts_dir="/home/ubuntu/repos/talos/src/talos/prompts",
            memory_file=str(memory_file)
        )
        
        print("✓ Agent initialized successfully")
        
        await agent.add_memory("User likes pizza", user_id="interactive-test")
        print("✓ Memory added: 'User likes pizza'")
        
        memories = agent.memory.search("pizza", user_id="interactive-test")
        if memories:
            print(f"✓ Memory retrieved: {memories[0].description}")
        else:
            print("✗ Failed to retrieve pizza memory")
        
        tool_names = [tool.name for tool in agent.tool_manager.tools.keys()]
        if "add_memory" in tool_names:
            print("✓ Memory tool available in agent tools")
        else:
            print("✗ Memory tool not found in agent tools")
        
        print("Interactive test completed successfully!")
            
    except Exception as e:
        print(f"✗ Interactive test failed: {e}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("Memory Integration Test Suite")
    print("=" * 40)
    
    asyncio.run(run_interactive_test())
    
    print("\nTo run full test suite:")
    print("uv run pytest test_memory_integration.py -v")
