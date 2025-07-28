from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import typer
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from talos.core.main_agent import MainAgent
from talos.core.router import Router
from talos.services.key_management import KeyManagement
from talos.settings import OpenAISettings
from talos.skills.proposals import ProposalsSkill
from talos.skills.twitter_persona import TwitterPersonaSkill
from talos.skills.twitter_sentiment import TwitterSentimentSkill
from talos.cli.daemon import TalosDaemon

app = typer.Typer()
twitter_app = typer.Typer()
app.add_typer(twitter_app, name="twitter")
proposals_app = typer.Typer()
app.add_typer(proposals_app, name="proposals")
github_app = typer.Typer()
app.add_typer(github_app, name="github")
memory_app = typer.Typer()
app.add_typer(memory_app, name="memory")


def get_repo_info(repo: Optional[str] = None) -> tuple[str, str]:
    """Get repository owner and name from CLI arg or environment variable."""
    repo_str = repo or os.getenv("GITHUB_REPO")
    if not repo_str:
        raise typer.BadParameter("Repository must be provided via --repo argument or GITHUB_REPO environment variable")
    
    if "/" not in repo_str:
        raise typer.BadParameter("Repository must be in format 'owner/repo'")
    
    owner, repo_name = repo_str.split("/", 1)
    return owner.strip(), repo_name.strip()


@github_app.command("get-prs")
def get_prs(
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository in format 'owner/repo'"),
    state: str = typer.Option("open", "--state", help="PR state: open, closed, or all")
):
    """List all pull requests for a repository."""
    try:
        from talos.tools.github.tools import GithubTools
        
        owner, repo_name = get_repo_info(repo)
        github_tools = GithubTools()
        prs = github_tools.get_all_pull_requests(owner, repo_name, state)
        
        if not prs:
            print(f"No {state} pull requests found in {owner}/{repo_name}")
            return
            
        print(f"=== {state.title()} Pull Requests for {owner}/{repo_name} ===")
        for pr in prs:
            print(f"#{pr['number']}: {pr['title']}")
            print(f"  URL: {pr['url']}")
            print()
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@github_app.command("review-pr")
def review_pr(
    pr_number: int = typer.Argument(..., help="Pull request number to review"),
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository in format 'owner/repo'"),
    post_review: bool = typer.Option(False, "--post", help="Post the review as a comment on the PR"),
    auto_approve: bool = typer.Option(False, "--auto-approve", help="Automatically approve if criteria are met")
):
    """Review a pull request using AI analysis."""
    try:
        from talos.skills.pr_review import PRReviewSkill
        from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
        from talos.tools.github.tools import GithubTools
        
        owner, repo_name = get_repo_info(repo)
        
        model = ChatOpenAI(model="gpt-4", temperature=0.0)
        prompt_manager = FilePromptManager("src/talos/prompts")
        github_tools = GithubTools()
        
        skill = PRReviewSkill(
            llm=model,
            prompt_manager=prompt_manager,
            github_tools=github_tools
        )
        
        response = skill.run(
            user=owner,
            repo=repo_name,
            pr_number=pr_number,
            auto_comment=post_review,
            auto_approve=auto_approve
        )
        
        print(f"=== PR Review for {owner}/{repo_name}#{pr_number} ===")
        print(response.answers[0])
        if response.security_score:
            print(f"\nSecurity Score: {response.security_score}/100")
        if response.quality_score:
            print(f"Quality Score: {response.quality_score}/100")
        if response.recommendation:
            print(f"Recommendation: {response.recommendation}")
        if response.reasoning:
            print(f"Reasoning: {response.reasoning}")
            
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@github_app.command("approve-pr")
def approve_pr(
    pr_number: int = typer.Argument(..., help="Pull request number to approve"),
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository in format 'owner/repo'")
):
    """Force approve a pull request."""
    try:
        from talos.tools.github.tools import GithubTools
        
        owner, repo_name = get_repo_info(repo)
        github_tools = GithubTools()
        
        github_tools.approve_pr(owner, repo_name, pr_number)
        print(f"✅ Approved PR #{pr_number} in {owner}/{repo_name}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@github_app.command("merge-pr")
def merge_pr(
    pr_number: int = typer.Argument(..., help="Pull request number to merge"),
    repo: Optional[str] = typer.Option(None, "--repo", "-r", help="Repository in format 'owner/repo'")
):
    """Merge a pull request."""
    try:
        from talos.tools.github.tools import GithubTools
        
        owner, repo_name = get_repo_info(repo)
        github_tools = GithubTools()
        
        github_tools.merge_pr(owner, repo_name, pr_number)
        print(f"🎉 Merged PR #{pr_number} in {owner}/{repo_name}")
        
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@proposals_app.command("eval")
def eval_proposal(
    filepath: str = typer.Option(..., "--file", "-f", help="Path to the proposal file."),
    model_name: str = "gpt-4",
    temperature: float = 0.0,
):
    """
    Evaluates a proposal from a file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found at {filepath}")
    model = ChatOpenAI(model=model_name, temperature=temperature)
    skill = ProposalsSkill(llm=model)
    response = skill.run(filepath=filepath)
    print(response.answers[0])


@twitter_app.command()
def get_user_prompt(username: str):
    """
    Gets the general voice of a user as a structured persona analysis.
    """
    skill = TwitterPersonaSkill()
    response = skill.run(username=username)
    
    print(f"=== Twitter Persona Analysis for @{username} ===\n")
    print(f"Report:\n{response.report}\n")
    print(f"Topics: {', '.join(response.topics)}\n")
    print(f"Style: {', '.join(response.style)}")


@twitter_app.command()
def get_query_sentiment(query: str, start_time: Optional[str] = None):
    """
    Gets the general sentiment/report on a specific query.

    Args:
        query: Search query for tweets
        start_time: Optional datetime filter (ISO 8601 format, e.g., "2023-01-01T00:00:00Z")
    """
    skill = TwitterSentimentSkill()
    response = skill.run(query=query, start_time=start_time)
    if response.score is not None:
        print(f"Sentiment Score: {response.score}/100")
        print("=" * 50)
    print(response.answers[0])


@app.callback()
def callback(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User identifier for conversation tracking."),
    use_database: bool = typer.Option(True, "--use-database", help="Use database for conversation storage instead of files."),
):
    """
    The main entry point for the Talos agent.
    """
    pass


@app.command("main")
def main_cli(
    query: Optional[str] = typer.Argument(None, help="The query to send to the agent."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User identifier for conversation tracking."),
    use_database: bool = typer.Option(True, "--use-database", help="Use database for conversation storage instead of files."),
):
    """
    Run the interactive Talos agent.
    """
    main_command(query=query, verbose=verbose, user_id=user_id, use_database=use_database)


@app.command(name="main")
def main_command(
    query: Optional[str] = typer.Argument(None, help="The query to send to the agent."),
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4",
    temperature: float = 0.0,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output."),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User identifier for conversation tracking."),
    use_database: bool = typer.Option(True, "--use-database", help="Use database for conversation storage instead of files."),
) -> None:
    """
    The main entry point for the Talos agent.
    """
    if not os.path.exists(prompts_dir):
        raise FileNotFoundError(f"Prompts directory not found at {prompts_dir}")

    OpenAISettings()

    # Create the main agent
    model = ChatOpenAI(model=model_name, temperature=temperature)
    router = Router([], [])
    main_agent = MainAgent(
        prompts_dir=prompts_dir,
        model=model,
        router=router,
        schema=None,
        user_id=user_id,
        use_database_memory=use_database,
        verbose=verbose,
    )
    
    if not user_id and use_database:
        print(f"Generated temporary user ID: {main_agent.user_id}")

    if query:
        # Run the agent
        result = main_agent.run(query)
        if isinstance(result, AIMessage):
            print(result.content)
        else:
            print(result)
        return

    # Interactive mode
    print("Entering interactive mode. Type 'exit' to quit.")
    while True:
        try:
            user_input = input(">> ")
            if user_input.lower() == "exit":
                break
            result = main_agent.run(user_input)
            if isinstance(result, AIMessage):
                has_tool_calls = hasattr(result, 'tool_calls') and result.tool_calls
                
                if result.content is not None and str(result.content).strip() and not has_tool_calls:
                    print(result.content)
                
                if has_tool_calls:
                    for tool_call in result.tool_calls:
                        try:
                            tool = main_agent.tool_manager.get_tool(tool_call['name'])
                            if tool:
                                tool_result = tool.invoke(tool_call['args'])
                                if verbose:
                                    print(f"🔧 Executed tool '{tool_call['name']}': {tool_result}")
                        except Exception as e:
                            if verbose:
                                print(f"❌ Tool execution error for '{tool_call['name']}': {e}")
                    
                    follow_up_prompt = f"The user just said: '{user_input}'. Please provide a brief, natural conversational response to what they said, as if you're having a normal conversation. Don't mention tools or memory - just respond naturally to their message."
                    
                    try:
                        from langchain_core.messages import SystemMessage, HumanMessage
                        follow_up_messages = [
                            SystemMessage(content="You are a helpful AI assistant having a natural conversation. Respond naturally to what the user said without mentioning any technical operations."),
                            HumanMessage(content=follow_up_prompt)
                        ]
                        follow_up_response = main_agent.model.invoke(follow_up_messages)
                        if hasattr(follow_up_response, 'content') and follow_up_response.content:
                            print(follow_up_response.content)
                        else:
                            print("Nice to meet you!")
                    except Exception:
                        print("Nice to meet you!")
            elif result is not None and not isinstance(result, AIMessage):
                print(result)
        except KeyboardInterrupt:
            break


@app.command()
def generate_keys(key_dir: str = ".keys"):
    """
    Generates a new RSA key pair.
    """
    km = KeyManagement(key_dir=key_dir)
    km.generate_keys()
    print(f"Keys generated in {key_dir}")


@app.command()
def get_public_key(key_dir: str = ".keys"):
    """
    Gets the public key.
    """
    km = KeyManagement(key_dir=key_dir)
    print(km.get_public_key())


@app.command()
def encrypt(data: str, public_key_file: str):
    """
    Encrypts a message.
    """
    with open(public_key_file, "rb") as f:
        public_key = f.read()

    import base64

    from nacl.public import PublicKey, SealedBox

    sealed_box = SealedBox(PublicKey(public_key))
    encrypted = sealed_box.encrypt(data.encode())
    print(base64.b64encode(encrypted).decode())


@app.command()
def decrypt(encrypted_data: str, key_dir: str = ".keys"):
    """
    Decrypts a message.
    """
    km = KeyManagement(key_dir=key_dir)
    import base64

    decoded_data = base64.b64decode(encrypted_data)
    print(km.decrypt(decoded_data))


@app.command()
def daemon(
    prompts_dir: str = "src/talos/prompts",
    model_name: str = "gpt-4",
    temperature: float = 0.0,
) -> None:
    """
    Run the Talos agent in daemon mode for continuous operation with scheduled jobs.
    """
    import asyncio
    
    daemon = TalosDaemon(
        prompts_dir=prompts_dir,
        model_name=model_name,
        temperature=temperature
    )
    asyncio.run(daemon.run())


@app.command()
def cleanup_users(
    older_than_hours: int = typer.Option(24, "--older-than", help="Remove temporary users inactive for this many hours."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deleted without actually deleting."),
) -> None:
    """
    Clean up temporary users and their conversation data.
    """
    from talos.database.utils import cleanup_temporary_users, get_user_stats
    
    if dry_run:
        stats = get_user_stats()
        print("Current database stats:")
        print(f"  Total users: {stats['total_users']}")
        print(f"  Permanent users: {stats['permanent_users']}")
        print(f"  Temporary users: {stats['temporary_users']}")
        print(f"\nWould clean up temporary users inactive for {older_than_hours} hours.")
        print("Use --no-dry-run to actually perform the cleanup.")
    else:
        count = cleanup_temporary_users(older_than_hours)
        print(f"Cleaned up {count} temporary users and their conversation data.")


@app.command()
def db_stats() -> None:
    """
    Show database statistics.
    """
    from talos.database.utils import get_user_stats
    
    stats = get_user_stats()
    print("Database Statistics:")
    print(f"  Total users: {stats['total_users']}")
    print(f"  Permanent users: {stats['permanent_users']}")
    print(f"  Temporary users: {stats['temporary_users']}")
    
    if stats['total_users'] > 0:
        temp_percentage = (stats['temporary_users'] / stats['total_users']) * 100
        print(f"  Temporary user percentage: {temp_percentage:.1f}%")


@memory_app.command("list")
def list_memories(
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User ID to filter memories by"),
    filter_user: Optional[str] = typer.Option(None, "--filter-user", help="Filter memories by a different user"),
    use_database: bool = typer.Option(True, "--use-database", help="Use database backend instead of files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """List all memories with optional user filtering."""
    try:
        from talos.core.memory import Memory
        from langchain_openai import OpenAIEmbeddings
        from talos.settings import OpenAISettings
        
        OpenAISettings()
        embeddings_model = OpenAIEmbeddings()
        
        if use_database:
            from talos.database.session import init_database
            init_database()
            
            if not user_id:
                import uuid
                user_id = str(uuid.uuid4())
                if verbose:
                    print(f"Generated temporary user ID: {user_id}")
            
            memory = Memory(
                embeddings_model=embeddings_model,
                user_id=user_id,
                session_id="cli-session",
                use_database=True,
                verbose=verbose
            )
        else:
            from pathlib import Path
            memory_dir = Path("memory")
            memory_dir.mkdir(exist_ok=True)
            
            memory = Memory(
                file_path=memory_dir / "memories.json",
                embeddings_model=embeddings_model,
                history_file_path=memory_dir / "history.json",
                use_database=False,
                verbose=verbose
            )
        
        memories = memory.list_all(filter_user_id=filter_user)
        
        if not memories:
            print("No memories found.")
            return
        
        print(f"=== Found {len(memories)} memories ===")
        for i, mem in enumerate(memories, 1):
            timestamp_str = datetime.fromtimestamp(mem.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i}. [{timestamp_str}] {mem.description}")
            if mem.metadata:
                print(f"   Metadata: {mem.metadata}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@memory_app.command("search")
def search_memories(
    query: str = typer.Argument(..., help="Search query for memories"),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User ID to search memories for"),
    filter_user: Optional[str] = typer.Option(None, "--filter-user", help="Filter memories by a different user"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results to return"),
    use_database: bool = typer.Option(True, "--use-database", help="Use database backend instead of files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Search memories using semantic similarity with optional user filtering."""
    try:
        from talos.core.memory import Memory
        from langchain_openai import OpenAIEmbeddings
        from talos.settings import OpenAISettings
        
        OpenAISettings()
        embeddings_model = OpenAIEmbeddings()
        
        if use_database:
            from talos.database.session import init_database
            init_database()
            
            if not user_id:
                import uuid
                user_id = str(uuid.uuid4())
                if verbose:
                    print(f"Generated temporary user ID: {user_id}")
            
            memory = Memory(
                embeddings_model=embeddings_model,
                user_id=user_id,
                session_id="cli-session",
                use_database=True,
                verbose=verbose
            )
        else:
            from pathlib import Path
            memory_dir = Path("memory")
            memory_dir.mkdir(exist_ok=True)
            
            memory = Memory(
                file_path=memory_dir / "memories.json",
                embeddings_model=embeddings_model,
                history_file_path=memory_dir / "history.json",
                use_database=False,
                verbose=verbose
            )
        
        if filter_user and use_database:
            memory = Memory(
                embeddings_model=embeddings_model,
                user_id=filter_user,
                session_id="cli-session",
                use_database=True,
                verbose=verbose
            )
        elif filter_user and not use_database:
            print("Warning: User filtering not supported with file-based backend")
        
        results = memory.search(query, k=limit)
        
        if not results:
            print(f"No memories found for query: '{query}'")
            return
        
        print(f"=== Search Results for '{query}' ({len(results)} found) ===")
        for i, mem in enumerate(results, 1):
            timestamp_str = datetime.fromtimestamp(mem.timestamp).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{i}. [{timestamp_str}] {mem.description}")
            if mem.metadata:
                print(f"   Metadata: {mem.metadata}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


@memory_app.command("flush")
def flush_memories(
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User ID for database backend. If not provided with database backend, flushes ALL memories."),
    use_database: bool = typer.Option(True, "--use-database", help="Use database backend instead of files"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Flush unsaved memories to disk. If no user_id provided with database backend, flushes ALL memories after confirmation."""
    try:
        from talos.core.memory import Memory
        from langchain_openai import OpenAIEmbeddings
        from talos.settings import OpenAISettings
        
        OpenAISettings()
        embeddings_model = OpenAIEmbeddings()
        
        if use_database:
            from talos.database.session import init_database
            from talos.database.memory_backend import DatabaseMemoryBackend
            init_database()
            
            if not user_id:
                if typer.confirm("⚠️  No user ID provided. This will DELETE ALL memories from the database. Are you sure?"):
                    deleted_count = DatabaseMemoryBackend.flush_all_memories()
                    print(f"Successfully deleted {deleted_count} memories from the database.")
                else:
                    print("Operation cancelled.")
                return
            else:
                deleted_count = DatabaseMemoryBackend.flush_user_memories(user_id)
                if deleted_count > 0:
                    print(f"Successfully deleted {deleted_count} memories for user '{user_id}' from the database.")
                else:
                    print(f"No memories found for user '{user_id}' or user does not exist.")
                return
            
            memory = Memory(
                embeddings_model=embeddings_model,
                user_id=user_id,
                session_id="cli-session",
                use_database=True,
                verbose=verbose
            )
        else:
            from pathlib import Path
            memory_dir = Path("memory")
            memory_dir.mkdir(exist_ok=True)
            
            memory = Memory(
                file_path=memory_dir / "memories.json",
                embeddings_model=embeddings_model,
                history_file_path=memory_dir / "history.json",
                use_database=False,
                verbose=verbose
            )
        
        if hasattr(memory, '_unsaved_count') and memory._unsaved_count > 0:
            unsaved_count = memory._unsaved_count
            memory.flush()
            print(f"Successfully flushed {unsaved_count} unsaved memories to disk.")
        else:
            print("No unsaved memories to flush.")
            
    except Exception as e:
        print(f"Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
