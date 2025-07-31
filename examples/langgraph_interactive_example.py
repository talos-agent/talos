#!/usr/bin/env python3
"""
Interactive LangGraph Agent Example

This example demonstrates a multi-step DAG (Directed Acyclic Graph) execution 
with branching logic using LangGraph. The agent can handle different types of 
queries and route them through appropriate processing nodes.

Features demonstrated:
- Multi-step DAG execution with StateGraph
- Conditional branching based on query content
- Memory persistence with MemorySaver
- Multiple node types (Router, Analysis, Processing, Output)
- Interactive CLI for testing different scenarios

Usage:
    python examples/langgraph_interactive_example.py
"""

import asyncio
from typing import Any, Dict, List, Literal, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END


class AgentState(TypedDict):
    """State that flows through the DAG nodes."""
    messages: List[BaseMessage]
    query: str
    query_type: str
    analysis_result: Dict[str, Any]
    processing_result: Dict[str, Any]
    final_output: str
    metadata: Dict[str, Any]


class InteractiveLangGraphAgent:
    """
    Interactive LangGraph agent demonstrating multi-step DAG execution with branching.
    
    The DAG flow:
    START -> query_analyzer -> router -> [sentiment_processor | proposal_processor | general_processor] -> output_formatter -> END
    """
    
    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model = ChatOpenAI(model=model_name, temperature=0.1)
        self.checkpointer = MemorySaver()
        self.graph = self._build_graph()
        
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph StateGraph with multiple nodes and conditional routing."""
        workflow = StateGraph(AgentState)
        
        workflow.add_node("query_analyzer", self._analyze_query)
        workflow.add_node("router", self._route_query)
        workflow.add_node("sentiment_processor", self._process_sentiment_query)
        workflow.add_node("proposal_processor", self._process_proposal_query)
        workflow.add_node("general_processor", self._process_general_query)
        workflow.add_node("output_formatter", self._format_output)
        
        workflow.add_edge(START, "query_analyzer")
        workflow.add_edge("query_analyzer", "router")
        
        workflow.add_conditional_edges(
            "router",
            self._determine_next_node,
            {
                "sentiment": "sentiment_processor",
                "proposal": "proposal_processor", 
                "general": "general_processor"
            }
        )
        
        workflow.add_edge("sentiment_processor", "output_formatter")
        workflow.add_edge("proposal_processor", "output_formatter")
        workflow.add_edge("general_processor", "output_formatter")
        
        workflow.add_edge("output_formatter", END)
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def _analyze_query(self, state: AgentState) -> AgentState:
        """Step 1: Analyze the incoming query to understand its intent and content."""
        query = state["query"]
        
        analysis_prompt = f"""
        Analyze the following query and provide structured analysis:
        Query: "{query}"
        
        Please analyze:
        1. Main topic/subject
        2. Intent (what the user wants to accomplish)
        3. Key entities mentioned
        4. Sentiment/tone
        5. Complexity level (simple/moderate/complex)
        
        Provide your analysis in a structured format.
        """
        
        response = await self.model.ainvoke([HumanMessage(content=analysis_prompt)])
        
        analysis_result = {
            "raw_analysis": response.content,
            "timestamp": "2025-01-31T04:13:49Z",
            "model_used": self.model.model_name
        }
        
        state["analysis_result"] = analysis_result
        state["messages"].append(AIMessage(content=f"Query analyzed: {query[:100]}..."))
        
        print(f"🔍 ANALYSIS STEP: Analyzed query - {query[:50]}...")
        return state
    
    async def _route_query(self, state: AgentState) -> AgentState:
        """Step 2: Route the query to appropriate processor based on content analysis."""
        query = state["query"].lower()
        
        if any(keyword in query for keyword in ["sentiment", "feeling", "opinion", "twitter", "social"]):
            query_type = "sentiment"
        elif any(keyword in query for keyword in ["proposal", "governance", "vote", "dao", "protocol"]):
            query_type = "proposal"
        else:
            query_type = "general"
        
        state["query_type"] = query_type
        state["messages"].append(AIMessage(content=f"Query routed to: {query_type} processor"))
        
        print(f"🔀 ROUTING STEP: Query type determined as '{query_type}'")
        return state
    
    def _determine_next_node(self, state: AgentState) -> Literal["sentiment", "proposal", "general"]:
        """Conditional edge function that determines which processor to use."""
        return state["query_type"]
    
    async def _process_sentiment_query(self, state: AgentState) -> AgentState:
        """Step 3a: Process sentiment-related queries with specialized logic."""
        query = state["query"]
        
        sentiment_prompt = f"""
        You are a sentiment analysis specialist. Analyze the following query for sentiment-related insights:
        Query: "{query}"
        
        Provide:
        1. Overall sentiment classification (positive/negative/neutral)
        2. Emotional indicators found
        3. Confidence level in your analysis
        4. Recommendations for response tone
        5. Key sentiment-bearing phrases
        
        Format your response as a structured analysis.
        """
        
        response = await self.model.ainvoke([HumanMessage(content=sentiment_prompt)])
        
        processing_result = {
            "processor_type": "sentiment",
            "analysis": response.content,
            "specialized_insights": "Sentiment patterns and emotional indicators identified",
            "confidence_score": 0.85
        }
        
        state["processing_result"] = processing_result
        state["messages"].append(AIMessage(content="Sentiment analysis completed"))
        
        print("💭 SENTIMENT PROCESSING: Analyzed emotional content and sentiment patterns")
        return state
    
    async def _process_proposal_query(self, state: AgentState) -> AgentState:
        """Step 3b: Process governance/proposal-related queries with specialized logic."""
        query = state["query"]
        
        proposal_prompt = f"""
        You are a governance and proposal analysis expert. Analyze the following query:
        Query: "{query}"
        
        Provide:
        1. Governance implications
        2. Stakeholder impact assessment
        3. Risk factors to consider
        4. Implementation complexity
        5. Community considerations
        6. Recommended evaluation criteria
        
        Format your response as a comprehensive governance analysis.
        """
        
        response = await self.model.ainvoke([HumanMessage(content=proposal_prompt)])
        
        processing_result = {
            "processor_type": "proposal",
            "analysis": response.content,
            "specialized_insights": "Governance implications and stakeholder impact assessed",
            "risk_level": "moderate"
        }
        
        state["processing_result"] = processing_result
        state["messages"].append(AIMessage(content="Proposal analysis completed"))
        
        print("🏛️ PROPOSAL PROCESSING: Analyzed governance implications and stakeholder impact")
        return state
    
    async def _process_general_query(self, state: AgentState) -> AgentState:
        """Step 3c: Process general queries with broad analytical approach."""
        query = state["query"]
        
        general_prompt = f"""
        You are a general purpose AI assistant. Provide a comprehensive response to:
        Query: "{query}"
        
        Provide:
        1. Direct answer to the query
        2. Additional context that might be helpful
        3. Related topics or considerations
        4. Actionable recommendations if applicable
        5. Follow-up questions that might be relevant
        
        Format your response to be helpful and informative.
        """
        
        response = await self.model.ainvoke([HumanMessage(content=general_prompt)])
        
        processing_result = {
            "processor_type": "general",
            "analysis": response.content,
            "specialized_insights": "General analysis with broad contextual understanding",
            "completeness_score": 0.90
        }
        
        state["processing_result"] = processing_result
        state["messages"].append(AIMessage(content="General analysis completed"))
        
        print("🔧 GENERAL PROCESSING: Provided comprehensive analysis and recommendations")
        return state
    
    async def _format_output(self, state: AgentState) -> AgentState:
        """Step 4: Format the final output combining all processing results."""
        query = state["query"]
        analysis = state["analysis_result"]
        processing = state["processing_result"]
        
        output_prompt = f"""
        Create a final formatted response based on the following processing pipeline:
        
        Original Query: "{query}"
        Query Type: {state["query_type"]}
        Analysis Result: {analysis["raw_analysis"][:200]}...
        Processing Result: {processing["analysis"][:200]}...
        
        Create a well-structured final response that:
        1. Directly addresses the user's query
        2. Incorporates insights from the analysis phase
        3. Includes specialized processing results
        4. Provides clear, actionable information
        5. Maintains appropriate tone for the query type
        
        Format as a professional, helpful response.
        """
        
        response = await self.model.ainvoke([HumanMessage(content=output_prompt)])
        
        state["final_output"] = response.content
        state["messages"].append(AIMessage(content="Final output formatted and ready"))
        
        print("📋 OUTPUT FORMATTING: Created final structured response")
        return state
    
    async def process_query(self, query: str, thread_id: str = "default") -> Dict[str, Any]:
        """Process a query through the complete DAG pipeline."""
        print(f"\n🚀 Starting DAG execution for query: '{query[:50]}...'")
        print("=" * 70)
        
        initial_state: AgentState = {
            "messages": [HumanMessage(content=query)],
            "query": query,
            "query_type": "",
            "analysis_result": {},
            "processing_result": {},
            "final_output": "",
            "metadata": {
                "thread_id": thread_id,
                "start_time": "2025-01-31T04:13:49Z"
            }
        }
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            final_state = await self.graph.ainvoke(initial_state, config=config)
            
            print("=" * 70)
            print("✅ DAG execution completed successfully!")
            
            return {
                "success": True,
                "query": query,
                "query_type": final_state["query_type"],
                "final_output": final_state["final_output"],
                "processing_steps": len(final_state["messages"]),
                "metadata": final_state["metadata"]
            }
            
        except Exception as e:
            print(f"❌ DAG execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    def get_graph_visualization(self) -> str:
        """Get a text visualization of the DAG structure."""
        return """
        LangGraph DAG Structure:
        
        START
          ↓
        query_analyzer (Step 1: Analyze query intent and content)
          ↓
        router (Step 2: Determine processing path)
          ↓
        ┌─────────────────┬─────────────────┬─────────────────┐
        ↓                 ↓                 ↓                 ↓
    sentiment_processor  proposal_processor  general_processor
    (Step 3a: Sentiment) (Step 3b: Governance) (Step 3c: General)
        ↓                 ↓                 ↓
        └─────────────────┼─────────────────┘
                          ↓
                    output_formatter (Step 4: Format final response)
                          ↓
                         END
        
        Branching Logic:
        - Sentiment keywords → sentiment_processor
        - Governance keywords → proposal_processor  
        - Everything else → general_processor
        """


async def interactive_demo():
    """Run an interactive demonstration of the LangGraph agent."""
    print("🤖 Interactive LangGraph Agent Demo")
    print("=" * 50)
    print("This demo shows a multi-step DAG with conditional branching.")
    print("The agent will route your queries through different processing paths.\n")
    
    agent = InteractiveLangGraphAgent()
    
    print(agent.get_graph_visualization())
    print("\n" + "=" * 50)
    
    example_queries = [
        "What's the sentiment around the latest protocol update on Twitter?",
        "I need help evaluating this governance proposal for the DAO",
        "Can you explain how blockchain consensus mechanisms work?",
        "The community seems really excited about the new features!",
        "What are the risks of implementing this treasury management proposal?"
    ]
    
    print("Example queries to try:")
    for i, query in enumerate(example_queries, 1):
        print(f"{i}. {query}")
    print("6. Enter your own custom query")
    print("0. Exit")
    
    while True:
        print("\n" + "-" * 50)
        choice = input("Select an option (0-6): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        elif choice in ["1", "2", "3", "4", "5"]:
            query = example_queries[int(choice) - 1]
            print(f"\n🎯 Selected query: {query}")
        elif choice == "6":
            query = input("Enter your custom query: ").strip()
            if not query:
                print("❌ Empty query, please try again.")
                continue
        else:
            print("❌ Invalid choice, please try again.")
            continue
        
        result = await agent.process_query(query, thread_id=f"demo_{choice}")
        
        if result["success"]:
            print("\n📊 RESULTS:")
            print(f"Query Type: {result['query_type']}")
            print(f"Processing Steps: {result['processing_steps']}")
            print("\n📝 Final Response:")
            print("-" * 30)
            print(result["final_output"])
            print("-" * 30)
        else:
            print(f"\n❌ Error: {result['error']}")


def main():
    """Main entry point for the interactive example."""
    try:
        asyncio.run(interactive_demo())
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        print("Make sure you have OPENAI_API_KEY set in your environment.")


if __name__ == "__main__":
    main()
