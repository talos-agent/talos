from datetime import datetime
from typing import Optional
import typer

memory_app = typer.Typer()


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
