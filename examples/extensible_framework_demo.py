#!/usr/bin/env python3
"""
Demo script showing the structured LangGraph framework for blockchain-native AI.

This script demonstrates:
1. Creating a StructuredMainAgent with deterministic DAG structure
2. Individual node upgrades with version compatibility checks
3. Blockchain-native serialization and state management
4. Deterministic delegation patterns with hash-based routing
5. Node rollback and upgrade validation
"""

import os
from pathlib import Path

from langchain_openai import ChatOpenAI

from talos.core.extensible_agent import StructuredMainAgent, SupportAgent
from talos.dag.structured_nodes import NodeVersion
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill


class AnalyticsSkill(Skill):
    """A skill for data analytics and reporting."""
    
    @property
    def name(self) -> str:
        return "analytics"
    
    def run(self, **kwargs) -> str:
        query = kwargs.get("current_query", "No query provided")
        agent_analysis = kwargs.get("agent_analysis", "No analysis")
        
        result = f"Analytics skill executed: '{query}'"
        if agent_analysis:
            result += f" with agent analysis: {agent_analysis[:100]}..."
        
        return result


class ResearchSkill(Skill):
    """A skill for research and information gathering."""
    
    @property
    def name(self) -> str:
        return "research"
    
    def run(self, **kwargs) -> str:
        query = kwargs.get("current_query", "No query provided")
        agent_domain = kwargs.get("agent_domain", "unknown")
        
        result = f"Research skill executed for {agent_domain} domain: '{query}'"
        
        return result


def main():
    """Demonstrate the structured framework capabilities."""
    print("🔗 Talos Structured Blockchain Framework Demo")
    print("=" * 50)
    
    model = ChatOpenAI(model="gpt-4o-mini")
    prompts_dir = Path(__file__).parent.parent / "src" / "talos" / "prompts"
    prompt_manager = FilePromptManager(str(prompts_dir))
    
    print("\n1. Creating StructuredMainAgent...")
    agent = StructuredMainAgent(
        model=model,
        prompts_dir=str(prompts_dir),
        prompt_manager=prompt_manager,
        verbose=True,
        use_database_memory=False
    )
    
    print(f"✅ Structured agent created with {len(agent.support_agents)} default support agents")
    
    print("\n2. Initial Structured DAG Status:")
    status = agent.get_structured_status()
    if 'dag_name' in status:
        print(f"   DAG name: {status['dag_name']}")
        print(f"   DAG version: {status['dag_version']}")
        print(f"   Total nodes: {status['total_nodes']}")
        print(f"   Delegation hash: {status['delegation_hash']}")
        print(f"   Blockchain ready: {status['blockchain_ready']}")
        
        for node_id, info in status['structured_nodes'].items():
            print(f"   - {node_id}: v{info['version']} (hash: {info['node_hash'][:8]}...)")
    else:
        print(f"   Status: {status}")
        print("   ⚠️  Structured DAG not properly initialized")
    
    print("\n3. Testing individual node status...")
    for domain in ["governance", "analytics"]:
        node_status = agent.get_node_status(domain)
        if "error" not in node_status:
            print(f"   {domain}: v{node_status['version']} - {node_status['upgrade_policy']} policy")
            print(f"     Keywords: {node_status['delegation_keywords']}")
        else:
            print(f"   {domain}: {node_status['error']}")
    
    print("\n4. Testing node upgrade validation...")
    new_version = NodeVersion(major=1, minor=1, patch=0)
    validation = agent.validate_upgrade("governance", new_version)
    print(f"   Governance upgrade to v{new_version}: {validation}")
    
    incompatible_version = NodeVersion(major=2, minor=0, patch=0)
    validation = agent.validate_upgrade("governance", incompatible_version)
    print(f"   Governance upgrade to v{incompatible_version}: {validation}")
    
    print("\n5. Testing blockchain serialization...")
    blockchain_data = agent.export_for_blockchain()
    if blockchain_data:
        print(f"   DAG version: {blockchain_data.get('dag_version')}")
        print(f"   Checksum: {blockchain_data.get('checksum', '')[:16]}...")
        print(f"   Nodes: {len(blockchain_data.get('nodes', {}))}")
        print(f"   Edges: {len(blockchain_data.get('edges', []))}")
    else:
        print("   ❌ Blockchain export failed")
    
    print("\n6. Testing structured delegation...")
    
    try:
        result = agent.delegate_task("Analyze governance proposal for voting")
        print(f"   ✅ Governance delegation: {str(result)[:100]}...")
    except Exception as e:
        print(f"   ❌ Governance delegation failed: {e}")
    
    try:
        result = agent.delegate_task("Generate analytics report on user data")
        print(f"   ✅ Analytics delegation: {str(result)[:100]}...")
    except Exception as e:
        print(f"   ❌ Analytics delegation failed: {e}")
    
    print("\n7. Testing node upgrade (compatible version)...")
    new_governance_agent = SupportAgent(
        name="governance_v2",
        domain="governance",
        description="Enhanced governance agent with improved consensus",
        architecture={
            "task_flow": ["validate", "analyze", "simulate", "execute", "confirm"],
            "decision_points": ["proposal_validity", "consensus_mechanism", "execution_safety", "rollback_plan"],
            "capabilities": ["proposal_validation", "consensus_coordination", "safe_execution", "simulation"]
        },
        delegation_keywords=["governance", "proposal", "vote", "consensus", "dao"],
        task_patterns=["validate proposal", "coordinate consensus", "execute governance", "simulate outcome"]
    )
    
    upgrade_version = NodeVersion(major=1, minor=1, patch=0)
    success = agent.upgrade_support_agent("governance", new_governance_agent, upgrade_version)
    if success:
        print(f"   ✅ Successfully upgraded governance agent to v{upgrade_version}")
        updated_status = agent.get_node_status("governance")
        print(f"     New version: {updated_status['version']}")
        print(f"     New hash: {updated_status['node_hash'][:8]}...")
    else:
        print("   ❌ Failed to upgrade governance agent")
    
    print("\n8. Testing rollback capability...")
    rollback_version = NodeVersion(major=1, minor=0, patch=0)
    rollback_success = agent.rollback_node("governance", rollback_version)
    if rollback_success:
        print(f"   ✅ Successfully rolled back governance agent to v{rollback_version}")
    else:
        print("   ❌ Failed to rollback governance agent")
    
    print("\n9. Final DAG Status:")
    final_status = agent.get_structured_status()
    print(f"   Total nodes: {final_status['total_nodes']}")
    print(f"   Delegation hash: {final_status['delegation_hash']}")
    
    for node_id, info in final_status['structured_nodes'].items():
        print(f"   - {node_id}: v{info['version']} (policy: {info['upgrade_policy']})")
    
    print("\n10. DAG Visualization:")
    try:
        viz = agent.get_dag_visualization()
        print(viz)
    except Exception as e:
        print(f"   DAG not available: {e}")
    
    print("\n🎉 Structured Framework Demo completed!")
    print("\nKey Features Demonstrated:")
    print("✅ Structured DAG structure with versioned nodes")
    print("✅ Individual node identification and upgrade")
    print("✅ Version compatibility validation")
    print("✅ Blockchain-native serialization")
    print("✅ Deterministic delegation with hash-based routing")
    print("✅ Node rollback capabilities")
    print("✅ Single component upgrade for blockchain AI")
    
    print("\n📋 Architecture Benefits:")
    print("🔹 Deterministic execution for reproducible results")
    print("🔹 Individual component upgrades without system downtime")
    print("🔹 Hash-based verification for integrity assurance")
    print("🔹 Blockchain-compatible serialization format")
    print("🔹 Safe upgrade paths with rollback capabilities")
    print("🔹 Comprehensive monitoring and status reporting")
    
    print("\n🚀 Next Steps:")
    print("• Integrate with blockchain storage systems")
    print("• Implement automated upgrade pipelines")
    print("• Add custom support agents for specific domains")
    print("• Deploy in production environments")
    print("• Monitor system performance and upgrade patterns")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable is required")
        exit(1)
    
    main()
