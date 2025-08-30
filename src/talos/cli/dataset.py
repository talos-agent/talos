import typer
from typing import Optional

dataset_app = typer.Typer()


@dataset_app.command("add")
def add_dataset(
    name: str = typer.Argument(..., help="Name for the dataset"),
    source: str = typer.Argument(..., help="IPFS hash or URL of the document"),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User ID for dataset isolation"),
    chunk_size: int = typer.Option(1000, "--chunk-size", help="Maximum size of each text chunk"),
    chunk_overlap: int = typer.Option(200, "--chunk-overlap", help="Number of characters to overlap between chunks"),
    use_database: bool = typer.Option(True, "--use-database", help="Use database backend for persistence"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Add a dataset from IPFS hash or URL with intelligent chunking."""
    try:
        from talos.data.dataset_manager import DatasetManager
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
            
            dataset_manager = DatasetManager(
                verbose=verbose,
                user_id=user_id,
                session_id="cli-session",
                use_database=True,
                embeddings=embeddings_model
            )
        else:
            dataset_manager = DatasetManager(verbose=verbose, embeddings=embeddings_model)
        
        try:
            existing = dataset_manager.get_dataset(name)
            print(f"❌ Dataset '{name}' already exists with {len(existing)} chunks")
            return
        except ValueError:
            pass
        
        if source.startswith(('http://', 'https://')):
            dataset_manager.add_document_from_url(name, source, chunk_size, chunk_overlap)
        else:
            dataset_manager.add_document_from_ipfs(name, source, chunk_size, chunk_overlap)
        
        print(f"✅ Successfully added dataset '{name}' from {source}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)


@dataset_app.command("remove")
def remove_dataset(
    name: str = typer.Argument(..., help="Name of the dataset to remove"),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User ID for dataset isolation"),
    use_database: bool = typer.Option(True, "--use-database", help="Use database backend"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Remove a dataset by name."""
    try:
        from talos.data.dataset_manager import DatasetManager
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
            
            dataset_manager = DatasetManager(
                verbose=verbose,
                user_id=user_id,
                session_id="cli-session",
                use_database=True,
                embeddings=embeddings_model
            )
        else:
            dataset_manager = DatasetManager(verbose=verbose, embeddings=embeddings_model)
        
        dataset_manager.remove_dataset(name)
        print(f"✅ Successfully removed dataset '{name}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)


@dataset_app.command("list")
def list_datasets(
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User ID for dataset isolation"),
    use_database: bool = typer.Option(True, "--use-database", help="Use database backend"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """List all datasets."""
    try:
        from talos.data.dataset_manager import DatasetManager
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
            
            dataset_manager = DatasetManager(
                verbose=verbose,
                user_id=user_id,
                session_id="cli-session",
                use_database=True,
                embeddings=embeddings_model
            )
        else:
            dataset_manager = DatasetManager(verbose=verbose, embeddings=embeddings_model)
        
        datasets = dataset_manager.get_all_datasets()
        
        if not datasets:
            print("No datasets found.")
            return
        
        print(f"=== Found {len(datasets)} datasets ===")
        for name, data in datasets.items():
            print(f"📊 {name}: {len(data)} chunks")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)


@dataset_app.command("search")
def search_datasets(
    query: str = typer.Argument(..., help="Search query"),
    user_id: Optional[str] = typer.Option(None, "--user-id", "-u", help="User ID for dataset isolation"),
    limit: int = typer.Option(5, "--limit", "-l", help="Maximum number of results"),
    use_database: bool = typer.Option(True, "--use-database", help="Use database backend"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Search datasets using semantic similarity."""
    try:
        from talos.data.dataset_manager import DatasetManager
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
            
            dataset_manager = DatasetManager(
                verbose=verbose,
                user_id=user_id,
                session_id="cli-session",
                use_database=True,
                embeddings=embeddings_model
            )
        else:
            dataset_manager = DatasetManager(verbose=verbose, embeddings=embeddings_model)
        
        results = dataset_manager.search(query, k=limit)
        
        if not results:
            print(f"No results found for query: '{query}'")
            return
        
        print(f"=== Search Results for '{query}' ({len(results)} found) ===")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result[:200]}...")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise typer.Exit(1)
