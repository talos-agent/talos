from typing import Optional
import os
import typer


def get_repo_info(repo: Optional[str] = None) -> tuple[str, str]:
    """Get repository owner and name from CLI arg or environment variable."""
    repo_str = repo or os.getenv("GITHUB_REPO")
    if not repo_str:
        raise typer.BadParameter("Repository must be provided via --repo argument or GITHUB_REPO environment variable")
    
    if "/" not in repo_str:
        raise typer.BadParameter("Repository must be in format 'owner/repo'")
    
    owner, repo_name = repo_str.split("/", 1)
    return owner.strip(), repo_name.strip()
