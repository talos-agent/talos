from __future__ import annotations

import asyncio
import time
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.language_models import BaseLanguageModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from pydantic import ConfigDict

from talos.prompts.prompt_manager import PromptManager
from talos.services.implementations.devin import DevinService
from talos.skills.base import Skill
from talos.tools.document_loader import DatasetSearchTool, DocumentLoaderTool
from talos.tools.github.tools import GithubTools


class CodebaseImplementationState(TypedDict):
    """State that flows through the codebase implementation workflow."""

    messages: List[BaseMessage]
    original_request: str
    repository_url: Optional[str]
    additional_context: str
    technology_stack: Optional[str]
    gathered_info: Dict[str, Any]
    tool_documentation: Dict[str, Any]
    plan: Dict[str, Any]
    user_approval: Optional[bool]
    user_feedback: Optional[str]
    task_breakdown: List[Dict[str, Any]]
    devin_session_id: Optional[str]
    progress_updates: List[Dict[str, Any]]
    final_result: Dict[str, Any]
    metadata: Dict[str, Any]


class CodebaseImplementationSkill(Skill):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    """
    A skill for implementing codebases using LangGraph workflow orchestration and Devin integration.

    This skill orchestrates a multi-step workflow:
    1. Information gathering from GitHub/internet
    2. Plan creation using reasoning
    3. User approval process
    4. Task breakdown into implementable steps
    5. Devin execution and monitoring
    """

    model_config = {"arbitrary_types_allowed": True}

    llm: BaseLanguageModel
    prompt_manager: PromptManager
    devin_service: Optional[DevinService] = None
    github_tools: Optional[GithubTools] = None
    document_loader: Optional[DocumentLoaderTool] = None
    dataset_search: Optional[DatasetSearchTool] = None

    _graph: Optional[StateGraph] = None
    _compiled_graph: Optional[Any] = None
    _checkpointer: Optional[MemorySaver] = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        try:
            if not self.document_loader:
                from talos.data.dataset_manager import DatasetManager

                dataset_manager = DatasetManager(verbose=False)
                self.document_loader = DocumentLoaderTool(dataset_manager)
            if not self.dataset_search:
                from talos.data.dataset_manager import DatasetManager

                dataset_manager = DatasetManager(verbose=False)
                self.dataset_search = DatasetSearchTool(dataset_manager)
        except Exception:
            pass
        self._setup_workflow()

    @property
    def name(self) -> str:
        return "codebase_implementation"

    def _setup_workflow(self) -> None:
        """Initialize the LangGraph StateGraph workflow."""
        self._checkpointer = MemorySaver()
        self._graph = StateGraph(CodebaseImplementationState)

        self._graph.add_node("information_gatherer", self._gather_information)
        self._graph.add_node("tool_documentation_analyzer", self._analyze_tool_documentation)
        self._graph.add_node("plan_creator", self._create_plan)
        self._graph.add_node("user_approval_handler", self._handle_user_approval)
        self._graph.add_node("task_breakdown", self._breakdown_tasks)
        self._graph.add_node("devin_executor", self._execute_with_devin)
        self._graph.add_node("progress_monitor", self._monitor_progress)

        self._graph.add_edge(START, "information_gatherer")
        self._graph.add_edge("information_gatherer", "tool_documentation_analyzer")
        self._graph.add_edge("tool_documentation_analyzer", "plan_creator")
        self._graph.add_edge("plan_creator", "user_approval_handler")

        self._graph.add_conditional_edges(
            "user_approval_handler",
            self._determine_approval_path,
            {"approved": "task_breakdown", "rejected": "plan_creator", "pending": END},
        )

        self._graph.add_edge("task_breakdown", "devin_executor")
        self._graph.add_edge("devin_executor", "progress_monitor")
        self._graph.add_edge("progress_monitor", END)

        self._compiled_graph = self._graph.compile(checkpointer=self._checkpointer)

    async def _gather_information(self, state: CodebaseImplementationState) -> CodebaseImplementationState:
        """Step 1: Gather information from GitHub and other sources."""
        repository_url = state.get("repository_url")
        request = state["original_request"]
        technology_stack = state.get("technology_stack", "")

        info_prompt = f"""
        You are an expert software architect tasked with gathering information for implementing: "{request}"
        
        Repository URL: {repository_url or "Not provided"}
        Technology Stack Requirements: {technology_stack or "Not specified"}
        
        Analyze and gather the following information:
        1. If repository URL is provided, analyze the codebase structure, technologies used, and existing patterns
        2. Identify key requirements from the implementation request
        3. Extract technology stack from repository or use provided stack requirements
        4. Research relevant technologies, frameworks, and best practices
        5. Consider potential challenges and dependencies
        6. Identify tools and libraries that will need documentation analysis
        
        Provide a comprehensive information summary that will inform the implementation plan.
        Focus on identifying specific tools, frameworks, and technologies that will be used.
        """

        gathered_info = {}
        identified_tools = []

        if repository_url and self.github_tools:
            try:
                repo_parts = repository_url.replace("https://github.com/", "").split("/")
                if len(repo_parts) >= 2:
                    owner, repo = repo_parts[0], repo_parts[1]

                    repo_info = {"owner": owner, "name": repo}
                    file_structure = self.github_tools.get_project_structure(owner, repo)
                    readme_content = self.github_tools.get_file_content(owner, repo, "README.md")

                    # Try to get package files to identify dependencies
                    package_files = []
                    for filename in ["package.json", "requirements.txt", "Cargo.toml", "go.mod", "pom.xml"]:
                        try:
                            content = self.github_tools.get_file_content(owner, repo, filename)
                            package_files.append({"filename": filename, "content": content})
                        except Exception:
                            continue

                    gathered_info["repository"] = {
                        "info": repo_info,
                        "structure": file_structure,
                        "readme": readme_content,
                        "package_files": package_files,
                    }

                    for package_file in package_files:
                        if package_file["filename"] == "package.json":
                            identified_tools.extend(["npm", "node.js", "javascript"])
                        elif package_file["filename"] == "requirements.txt":
                            identified_tools.extend(["pip", "python"])
                        elif package_file["filename"] == "Cargo.toml":
                            identified_tools.extend(["cargo", "rust"])
                        elif package_file["filename"] == "go.mod":
                            identified_tools.extend(["go"])
                        elif package_file["filename"] == "pom.xml":
                            identified_tools.extend(["maven", "java"])

            except Exception as e:
                gathered_info["repository_error"] = str(e)  # type: ignore[assignment]

        if technology_stack:
            stack_tools = [tool.strip().lower() for tool in technology_stack.split(",")]
            identified_tools.extend(stack_tools)

        response = await self.llm.ainvoke([HumanMessage(content=info_prompt)])
        gathered_info["analysis"] = str(response.content if response.content else "")  # type: ignore[assignment]
        gathered_info["identified_tools"] = list(set(identified_tools))  # type: ignore[assignment]
        gathered_info["timestamp"] = float(time.time())  # type: ignore[assignment]

        state["gathered_info"] = gathered_info
        state["messages"].append(AIMessage(content="Information gathering completed"))

        return state

    async def _analyze_tool_documentation(self, state: CodebaseImplementationState) -> CodebaseImplementationState:
        """Step 2: Analyze tool documentation for identified technologies."""
        identified_tools = state["gathered_info"].get("identified_tools", [])

        tool_documentation = {}

        if identified_tools and self.document_loader:
            doc_analysis_prompt = f"""
            You are a technical documentation analyst. For the following tools/technologies: {", ".join(identified_tools)}
            
            Identify the most important documentation URLs that should be analyzed for implementation guidance.
            Focus on:
            1. Official documentation sites
            2. Getting started guides
            3. API references
            4. Best practices documentation
            5. Integration guides
            
            Provide a list of URLs for each tool that would be most valuable for implementation planning.
            Format as: Tool: [url1, url2, ...]
            """

            try:
                response = await self.llm.ainvoke([HumanMessage(content=doc_analysis_prompt)])
                doc_urls_analysis = response.content

                tool_documentation["url_analysis"] = doc_urls_analysis
                tool_documentation["identified_tools"] = identified_tools

                if self.dataset_search:
                    for tool in identified_tools[:3]:  # Limit to first 3 tools to avoid too many requests
                        try:
                            search_results = self.dataset_search.invoke(
                                {"query": f"{tool} documentation implementation guide"}
                            )
                            tool_documentation[f"{tool}_search_results"] = search_results
                        except Exception as e:
                            tool_documentation[f"{tool}_search_error"] = str(e)

            except Exception as e:
                tool_documentation["analysis_error"] = str(e)

        tool_documentation["timestamp"] = time.time()
        state["tool_documentation"] = tool_documentation
        state["messages"].append(AIMessage(content="Tool documentation analysis completed"))

        return state

    async def _create_plan(self, state: CodebaseImplementationState) -> CodebaseImplementationState:
        """Step 3: Create a detailed implementation plan using reasoning."""
        request = state["original_request"]
        gathered_info = state["gathered_info"]
        tool_documentation = state["tool_documentation"]
        user_feedback = state.get("user_feedback", "")
        technology_stack = state.get("technology_stack", "")

        plan_prompt = f"""
        You are an expert software architect. Create a detailed implementation plan for: "{request}"
        
        Available Information:
        {gathered_info.get("analysis", "No analysis available")}
        
        Repository Context:
        {gathered_info.get("repository", {}).get("readme", "No repository context")}
        
        Identified Tools/Technologies:
        {", ".join(gathered_info.get("identified_tools", []))}
        
        Technology Stack Requirements:
        {technology_stack or "Not specified - use best practices"}
        
        Tool Documentation Analysis:
        {tool_documentation.get("url_analysis", "No documentation analysis available")}
        
        User Feedback (if any):
        {user_feedback}
        
        Create a comprehensive implementation plan with:
        1. **Overview**: Clear summary of what will be implemented
        2. **Technology Stack**: Specific tools, frameworks, and versions to use
        3. **Architecture**: High-level design and approach based on identified tools
        4. **Key Components**: Main modules/files that need to be created or modified
        5. **Implementation Steps**: Logical sequence of development tasks
        6. **Dependencies**: Required libraries, tools, or external services with versions
        7. **Documentation References**: Key documentation that should be consulted
        8. **Testing Strategy**: How the implementation will be tested
        9. **Potential Risks**: Challenges and mitigation strategies
        10. **Timeline Estimate**: Rough effort estimation
        
        Ensure the plan leverages the identified tools and follows their best practices.
        Format your response as a structured plan that can be easily reviewed and approved.
        """

        response = await self.llm.ainvoke([HumanMessage(content=plan_prompt)])

        plan = {
            "content": response.content,
            "created_at": time.time(),
            "version": len(state.get("progress_updates", [])) + 1,
            "technology_stack": gathered_info.get("identified_tools", []),
            "documentation_references": tool_documentation,
        }

        state["plan"] = plan
        state["messages"].append(AIMessage(content="Implementation plan created"))

        return state

    async def _handle_user_approval(self, state: CodebaseImplementationState) -> CodebaseImplementationState:
        """Step 3: Handle user approval process."""
        plan_content = state["plan"]["content"]

        approval_message = f"""
        
        {plan_content}
        
        ---
        
        **Please review the above implementation plan and provide your approval:**
        - Type 'approve' to proceed with implementation
        - Type 'reject' with feedback to revise the plan
        - The workflow will wait for your response
        """

        state["messages"].append(AIMessage(content=approval_message))
        state["user_approval"] = None

        return state

    def _determine_approval_path(self, state: CodebaseImplementationState) -> str:
        """Determine the next step based on user approval status."""
        approval = state.get("user_approval")
        if approval is True:
            return "approved"
        elif approval is False:
            return "rejected"
        else:
            return "pending"

    async def _breakdown_tasks(self, state: CodebaseImplementationState) -> CodebaseImplementationState:
        """Step 4: Break down the approved plan into Devin-implementable tasks."""
        plan_content = state["plan"]["content"]

        breakdown_prompt = f"""
        You are a project manager breaking down an implementation plan into discrete, actionable tasks for a Devin AI agent.
        
        Implementation Plan:
        {plan_content}
        
        Break this down into specific, actionable tasks that can be implemented by Devin. Each task should:
        1. Be self-contained and clearly defined
        2. Include specific file paths and code changes needed
        3. Have clear acceptance criteria
        4. Be ordered logically with dependencies considered
        5. Be implementable within a reasonable time frame
        
        Format each task as:
        - **Task N**: Brief title
        - **Description**: Detailed description of what needs to be done
        - **Files**: Specific files to create/modify
        - **Acceptance Criteria**: How to verify the task is complete
        - **Dependencies**: Any previous tasks that must be completed first
        
        Provide 5-10 well-defined tasks that cover the complete implementation.
        """

        response = await self.llm.ainvoke([HumanMessage(content=breakdown_prompt)])

        task_breakdown = [
            {"id": i + 1, "content": task_content, "status": "pending", "created_at": time.time()}
            for i, task_content in enumerate(response.content.split("**Task")[1:])
        ]

        state["task_breakdown"] = task_breakdown
        state["messages"].append(AIMessage(content=f"Plan broken down into {len(task_breakdown)} tasks"))

        return state

    async def _execute_with_devin(self, state: CodebaseImplementationState) -> CodebaseImplementationState:
        """Step 5: Execute tasks using Devin service."""
        if not self.devin_service:
            state["final_result"] = {"success": False, "error": "Devin service not available", "timestamp": time.time()}
            return state

        task_breakdown = state["task_breakdown"]
        repository_url = state.get("repository_url", "")

        session_description = f"""
        Implement codebase features based on the following task breakdown:
        
        Repository: {repository_url}
        Original Request: {state["original_request"]}
        
        Tasks to implement:
        """

        for task in task_breakdown:
            session_description += f"\n{task['content']}"

        try:
            session_result = self.devin_service.create_session(description=session_description, idempotent=True)

            session_id = session_result.get("session_id")
            state["devin_session_id"] = session_id
            state["messages"].append(AIMessage(content=f"Devin session created: {session_id}"))

        except Exception as e:
            state["final_result"] = {
                "success": False,
                "error": f"Failed to create Devin session: {str(e)}",
                "timestamp": time.time(),
            }

        return state

    async def _monitor_progress(self, state: CodebaseImplementationState) -> CodebaseImplementationState:
        """Step 6: Monitor Devin session progress."""
        session_id = state.get("devin_session_id")

        if not session_id or not self.devin_service:
            state["final_result"] = {"success": False, "error": "No Devin session to monitor", "timestamp": time.time()}
            return state

        try:
            session_info = self.devin_service.get_session_info(session_id)

            progress_update = {
                "session_id": session_id,
                "status": session_info.get("status", "unknown"),
                "progress": session_info.get("progress", {}),
                "timestamp": time.time(),
            }

            if "progress_updates" not in state:
                state["progress_updates"] = []
            state["progress_updates"].append(progress_update)

            state["final_result"] = {
                "success": True,
                "devin_session_id": session_id,
                "session_status": session_info.get("status"),
                "progress_updates": state["progress_updates"],
                "timestamp": time.time(),
            }

            state["messages"].append(AIMessage(content=f"Progress monitoring completed for session {session_id}"))

        except Exception as e:
            state["final_result"] = {
                "success": False,
                "error": f"Failed to monitor session: {str(e)}",
                "timestamp": time.time(),
            }

        return state

    def run(self, **kwargs: Any) -> Any:
        """
        Execute the codebase implementation workflow.

        Args:
            implementation_request: Description of what to implement
            repository_url: Optional GitHub repository URL
            additional_context: Optional additional context or requirements
            technology_stack: Optional comma-separated list of required technologies/tools

        Returns:
            Dictionary containing workflow results and Devin session information
        """
        implementation_request = kwargs.get("implementation_request", "")
        repository_url = kwargs.get("repository_url")
        additional_context = kwargs.get("additional_context", "")

        if not implementation_request:
            return {"success": False, "error": "implementation_request is required"}

        initial_state: CodebaseImplementationState = {
            "messages": [HumanMessage(content=implementation_request)],
            "original_request": implementation_request,
            "repository_url": repository_url,
            "additional_context": additional_context,
            "technology_stack": kwargs.get("technology_stack"),
            "gathered_info": {},
            "tool_documentation": {},
            "plan": {},
            "user_approval": None,
            "user_feedback": None,
            "task_breakdown": [],
            "devin_session_id": None,
            "progress_updates": [],
            "final_result": {},
            "metadata": {"start_time": time.time(), "workflow_version": "1.1"},
        }

        thread_id = f"codebase_impl_{int(time.time())}"
        config = {"configurable": {"thread_id": thread_id}}

        try:
            if not self._compiled_graph:
                return {"success": False, "error": "Workflow not properly initialized"}

            try:
                asyncio.get_running_loop()
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._compiled_graph.ainvoke(initial_state, config=config))
                    final_state = future.result()
            except RuntimeError:
                final_state = asyncio.run(self._compiled_graph.ainvoke(initial_state, config=config))

            return final_state.get(
                "final_result", {"success": True, "message": "Workflow completed", "thread_id": thread_id}
            )

        except Exception as e:
            return {"success": False, "error": f"Workflow execution failed: {str(e)}"}

    def approve_plan(self, thread_id: str, approved: bool, feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Approve or reject a plan for a specific workflow thread.

        Args:
            thread_id: The workflow thread ID
            approved: Whether the plan is approved
            feedback: Optional feedback for plan revision

        Returns:
            Result of the approval action
        """
        if not self._compiled_graph:
            return {"success": False, "error": "Workflow not initialized"}

        try:
            config = {"configurable": {"thread_id": thread_id}}

            current_state = self._compiled_graph.get_state(config)
            if not current_state:
                return {"success": False, "error": "Thread not found"}

            state_values = current_state.values
            state_values["user_approval"] = approved
            if feedback:
                state_values["user_feedback"] = feedback

            self._compiled_graph.update_state(config, state_values)

            return {
                "success": True,
                "approved": approved,
                "thread_id": thread_id,
                "next_step": "task_breakdown" if approved else "plan_creator",
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to update approval: {str(e)}"}

    def get_workflow_status(self, thread_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow thread.

        Args:
            thread_id: The workflow thread ID

        Returns:
            Current workflow status and state
        """
        if not self._compiled_graph:
            return {"success": False, "error": "Workflow not initialized"}

        try:
            config = {"configurable": {"thread_id": thread_id}}
            current_state = self._compiled_graph.get_state(config)

            if not current_state:
                return {"success": False, "error": "Thread not found"}

            state_values = current_state.values

            return {
                "success": True,
                "thread_id": thread_id,
                "current_step": current_state.next,
                "plan": state_values.get("plan", {}),
                "devin_session_id": state_values.get("devin_session_id"),
                "progress_updates": state_values.get("progress_updates", []),
                "final_result": state_values.get("final_result", {}),
            }

        except Exception as e:
            return {"success": False, "error": f"Failed to get status: {str(e)}"}
