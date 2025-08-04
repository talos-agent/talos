from typing import Any
import time
import logging

from github import Auth, Github
from pydantic import BaseModel, Field, PrivateAttr

from ...settings import GitHubSettings
from ...utils.validation import validate_github_username, validate_github_repo_name, mask_sensitive_data
from ...utils.http_client import SecureHTTPClient

logger = logging.getLogger(__name__)


class GithubTools(BaseModel):
    """
    A collection of tools for interacting with the Github API.
    """

    token: str | None = Field(default_factory=lambda: GitHubSettings().GITHUB_API_TOKEN)
    _github: Github = PrivateAttr()
    _http_client: SecureHTTPClient = PrivateAttr()
    _headers: dict[str, str] = PrivateAttr()
    _repo_cache: dict[str, tuple[Any, float]] = PrivateAttr(default_factory=dict)
    _cache_ttl: int = PrivateAttr(default=300)

    def model_post_init(self, __context: Any) -> None:
        if not self.token:
            raise ValueError("Github token not provided.")
        
        self._github = Github(auth=Auth.Token(self.token))
        self._http_client = SecureHTTPClient()
        self._headers = {"Authorization": f"token {self.token}"}
        
        masked_token = mask_sensitive_data(self.token)
        logger.info(f"GitHub client initialized with token: {masked_token}")

    def _validate_repo_params(self, user: str, project: str) -> None:
        """Validate repository parameters."""
        if not validate_github_username(user):
            raise ValueError(f"Invalid GitHub username: {user}")
        if not validate_github_repo_name(project):
            raise ValueError(f"Invalid GitHub repository name: {project}")

    def _get_repo_cached(self, repo_key: str):
        """Get repository with caching to avoid repeated API calls."""
        current_time = time.time()
        
        if repo_key in self._repo_cache:
            repo, cached_time = self._repo_cache[repo_key]
            if current_time - cached_time < self._cache_ttl:
                return repo
        
        repo = self._github.get_repo(repo_key)
        self._repo_cache[repo_key] = (repo, current_time)
        return repo

    def get_open_issues(self, user: str, project: str) -> list[dict[str, Any]]:
        """
        Gets all open issues for a given repository.
        """
        self._validate_repo_params(user, project)
        repo = self._get_repo_cached(f"{user}/{project}")
        return [
            {"number": issue.number, "title": issue.title, "url": issue.html_url}
            for issue in repo.get_issues(state="open")
        ]

    def get_all_pull_requests(self, user: str, project: str, state: str = "open") -> list[dict[str, Any]]:
        """
        Gets all pull requests for a given repository.

        :param state: Can be one of 'open', 'closed', or 'all'.
        """
        self._validate_repo_params(user, project)
        if state not in ["open", "closed", "all"]:
            raise ValueError(f"Invalid state: {state}. Must be 'open', 'closed', or 'all'")
        repo = self._get_repo_cached(f"{user}/{project}")
        return [{"number": pr.number, "title": pr.title, "url": pr.html_url} for pr in repo.get_pulls(state=state)]

    def get_issue_comments(self, user: str, project: str, issue_number: int) -> list[dict[str, Any]]:
        """
        Gets all comments for a given issue.
        """
        self._validate_repo_params(user, project)
        if not isinstance(issue_number, int) or issue_number <= 0:
            raise ValueError(f"Invalid issue number: {issue_number}")
        repo = self._get_repo_cached(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        comments = []
        for comment in issue.get_comments():
            comments.append(
                {
                    "user": comment.user.login,
                    "comment": comment.body,
                    "reply_to": None,
                }
            )
        return comments

    def get_pr_comments(self, user: str, project: str, pr_number: int) -> list[dict[str, Any]]:
        """
        Gets all comments for a given pull request.
        """
        self._validate_repo_params(user, project)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"Invalid PR number: {pr_number}")
        repo = self._get_repo_cached(f"{user}/{project}")
        pr = repo.get_pull(pr_number)
        comments = []
        for comment in pr.get_issue_comments():
            comments.append(
                {
                    "user": comment.user.login,
                    "comment": comment.body,
                }
            )
        return comments

    def reply_to_issue(self, user: str, project: str, issue_number: int, comment: str) -> None:
        """
        Replies to a given issue.
        """
        self._validate_repo_params(user, project)
        if not isinstance(issue_number, int) or issue_number <= 0:
            raise ValueError(f"Invalid issue number: {issue_number}")
        if not comment or not comment.strip():
            raise ValueError("Comment cannot be empty")
        from ...utils.validation import sanitize_user_input
        comment = sanitize_user_input(comment, max_length=65536)
        repo = self._get_repo_cached(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)

    def get_pr_files(self, user: str, project: str, pr_number: int) -> list[str]:
        """
        Gets all files for a given pull request.
        """
        self._validate_repo_params(user, project)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"Invalid PR number: {pr_number}")
        repo = self._get_repo_cached(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        return [file.filename for file in pr.get_files()]

    def get_pr_diff(self, user: str, project: str, pr_number: int) -> str:
        """
        Gets the diff for a given pull request.
        """
        self._validate_repo_params(user, project)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"Invalid PR number: {pr_number}")
        repo = self._get_repo_cached(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        response = self._http_client.get(pr.patch_url, headers=self._headers)
        return response.text

    def get_project_structure(self, user: str, project: str, path: str = "") -> list[str]:
        """
        Gets the project structure for a given repository.
        """
        self._validate_repo_params(user, project)
        from ...utils.validation import sanitize_user_input
        path = sanitize_user_input(path, max_length=255)
        repo = self._get_repo_cached(f"{user}/{project}")
        contents = repo.get_contents(path)
        if isinstance(contents, list):
            return [content.path for content in contents]
        return [contents.path]

    def get_file_content(self, user: str, project: str, filepath: str) -> str:
        """
        Gets the content of a file.
        """
        self._validate_repo_params(user, project)
        if not filepath or not filepath.strip():
            raise ValueError("Filepath cannot be empty")
        from ...utils.validation import sanitize_user_input
        filepath = sanitize_user_input(filepath, max_length=255)
        repo = self._get_repo_cached(f"{user}/{project}")
        content = repo.get_contents(filepath)
        if isinstance(content, list):
            raise ValueError("Path is a directory, not a file.")
        return content.decoded_content.decode()

    def merge_pr(self, user: str, project: str, pr_number: int) -> None:
        """
        Merges a pull request.
        """
        self._validate_repo_params(user, project)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"Invalid PR number: {pr_number}")
        repo = self._get_repo_cached(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.merge()

    def review_pr(self, user: str, project: str, pr_number: int, feedback: str) -> None:
        """
        Reviews a pull request.
        """
        self._validate_repo_params(user, project)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"Invalid PR number: {pr_number}")
        if not feedback or not feedback.strip():
            raise ValueError("Feedback cannot be empty")
        from ...utils.validation import sanitize_user_input
        feedback = sanitize_user_input(feedback, max_length=65536)
        repo = self._get_repo_cached(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_review(body=feedback, event="COMMENT")

    def comment_on_pr(self, user: str, project: str, pr_number: int, comment: str) -> None:
        """
        Comments on a pull request.
        """
        self._validate_repo_params(user, project)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"Invalid PR number: {pr_number}")
        if not comment or not comment.strip():
            raise ValueError("Comment cannot be empty")
        from ...utils.validation import sanitize_user_input
        comment = sanitize_user_input(comment, max_length=65536)
        repo = self._get_repo_cached(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_issue_comment(comment)

    def approve_pr(self, user: str, project: str, pr_number: int) -> None:
        """
        Approves a pull request.
        """
        self._validate_repo_params(user, project)
        if not isinstance(pr_number, int) or pr_number <= 0:
            raise ValueError(f"Invalid PR number: {pr_number}")
        repo = self._get_repo_cached(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_review(event="APPROVE")

    def create_issue(self, user: str, project: str, title: str, body: str) -> dict[str, Any]:
        """
        Creates a new issue.
        """
        self._validate_repo_params(user, project)
        if not title or not title.strip():
            raise ValueError("Issue title cannot be empty")
        if not body or not body.strip():
            raise ValueError("Issue body cannot be empty")
        from ...utils.validation import sanitize_user_input
        title = sanitize_user_input(title, max_length=256)
        body = sanitize_user_input(body, max_length=65536)
        repo = self._get_repo_cached(f"{user}/{project}")
        issue = repo.create_issue(title=title, body=body)
        return {"number": issue.number, "title": issue.title, "url": issue.html_url}
