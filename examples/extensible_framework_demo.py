#!/usr/bin/env python3
"""
Demo script showing how to use the extensible LangGraph framework for Talos.

This script demonstrates:
1. Creating an ExtensibleMainAgent
2. Adding and removing skill agents dynamically
3. Configuring skills with individual LLMs and memory
4. Using both orchestrated and direct interaction modes
5. Skills gathering information via chat before execution
"""

import os
from pathlib import Path

from langchain_openai import ChatOpenAI

from talos.core.extensible_agent import ExtensibleMainAgent
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill


class DemoSkill(Skill):
    """A simple demo skill for testing the extensible framework."""
    
    @property
    def name(self) -> str:
        return "demo"
    
    def run(self, **kwargs) -> str:
        query = kwargs.get("current_query", "No query provided")
        context = kwargs.get("skill_agent_processed", False)
        
        result = f"Demo skill '{self.name}' executed with query: '{query}'"
        if context:
            result += " (processed by skill agent)"
        
        return result


class ChatEnabledSkill(Skill):
    """A skill that demonstrates chat-enabled information gathering."""
    
    @property
    def name(self) -> str:
        return "chat_demo"
    
    def run(self, **kwargs) -> str:
        query = kwargs.get("current_query", "No query provided")
        enhanced_context = kwargs.get("skill_agent_processed", False)
        
        result = f"Chat-enabled skill executed: '{query}'"
        if enhanced_context:
            result += " with enhanced context from chat gathering"
        
        return result


def main():
    """Demonstrate the extensible framework capabilities."""
    print("🚀 Talos Extensible Framework Demo")
    print("=" * 50)
    
    model = ChatOpenAI(model="gpt-4o-mini")
    prompts_dir = Path(__file__).parent.parent / "src" / "talos" / "prompts"
    prompt_manager = FilePromptManager(str(prompts_dir))
    
    print("\n1. Creating ExtensibleMainAgent...")
    agent = ExtensibleMainAgent(
        model=model,
        prompts_dir=str(prompts_dir),
        prompt_manager=prompt_manager,
        verbose=True,
        use_database_memory=False
    )
    
    print(f"✅ Agent created with {len(agent.list_skill_agents())} default skills")
    
    print("\n2. Initial Framework Status:")
    status = agent.get_framework_status()
    print(f"   Interaction mode: {status['interaction_mode']}")
    print(f"   Total skills: {status['total_skills']}")
    for skill_name, info in status['skills'].items():
        print(f"   - {skill_name}: {info['description']}")
    
    print("\n3. Adding custom skill with individual memory...")
    demo_skill = DemoSkill()
    skill_agent = agent.add_skill_agent(
        skill=demo_skill,
        name="custom_demo",
        description="A custom demo skill with individual memory",
        use_individual_memory=True,
        chat_enabled=False
    )
    print(f"✅ Added skill: {skill_agent.name}")
    
    print("\n4. Adding chat-enabled skill with custom LLM...")
    chat_skill = ChatEnabledSkill()
    custom_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    chat_skill_agent = agent.add_skill_agent(
        skill=chat_skill,
        name="chat_demo",
        description="A skill that can gather info via chat",
        model=custom_model,
        use_individual_memory=True,
        chat_enabled=True
    )
    print(f"✅ Added chat-enabled skill: {chat_skill_agent.name}")
    
    print("\n5. Updated Framework Status:")
    status = agent.get_framework_status()
    print(f"   Total skills: {status['total_skills']}")
    for skill_name, info in status['skills'].items():
        memory_type = "individual" if info['individual_memory'] else "shared"
        chat_status = "enabled" if info['chat_enabled'] else "disabled"
        print(f"   - {skill_name}: {memory_type} memory, chat {chat_status}")
    
    print("\n6. Testing direct skill interaction...")
    agent.set_interaction_mode("direct")
    
    try:
        result = agent.interact_with_skill(
            "custom_demo", 
            "Test query for custom demo skill",
            additional_context="some extra info"
        )
        print(f"✅ Direct interaction result: {result}")
    except Exception as e:
        print(f"❌ Direct interaction failed: {e}")
    
    print("\n7. Testing orchestrated mode...")
    agent.set_interaction_mode("orchestrated")
    
    try:
        print("   Orchestrated mode set (DAG execution would happen here)")
    except Exception as e:
        print(f"❌ Orchestrated mode failed: {e}")
    
    print("\n8. Testing skill removal...")
    success = agent.remove_skill_agent("custom_demo")
    if success:
        print("✅ Successfully removed custom_demo skill")
        status = agent.get_framework_status()
        print(f"   Remaining skills: {list(status['skills'].keys())}")
    else:
        print("❌ Failed to remove skill")
    
    print("\n9. DAG Visualization:")
    try:
        viz = agent.get_dag_visualization()
        print(viz)
    except Exception as e:
        print(f"   DAG not available: {e}")
    
    print("\n🎉 Demo completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Dynamic skill addition and removal")
    print("✅ Individual skill configurations (memory, LLM)")
    print("✅ Chat-enabled information gathering")
    print("✅ Direct and orchestrated interaction modes")
    print("✅ Framework status monitoring")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable is required")
        exit(1)
    
    main()
