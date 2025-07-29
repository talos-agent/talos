from typing import Optional
import typer
from langchain_openai import ChatOpenAI

from talos.cli.utils import get_repo_info

github_app = typer.Typer()


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
