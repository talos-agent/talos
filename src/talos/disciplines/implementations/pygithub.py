from github import Github
from talos.disciplines.abstract.github import GitHub


class PyGithubDiscipline(GitHub):
    """
    A discipline for interacting with GitHub using PyGithub.
    """

    def __init__(self, token: str):
        self.github = Github(token)

    def read_issue(self, issue_url: str) -> str:
        """
        Reads a GitHub issue.
        """
        repo_name, issue_number = self._extract_repo_and_issue_number(issue_url)
        repo = self.github.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number)
        return issue.body

    def reply_to_issue(self, issue_url: str, comment: str) -> None:
        """
        Replies to a GitHub issue.
        """
        repo_name, issue_number = self._extract_repo_and_issue_number(issue_url)
        repo = self.github.get_repo(repo_name)
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)

    def review_pr(self, pr_url: str, feedback: str) -> None:
        """
        Reviews a pull request.
        """
        repo_name, pr_number = self._extract_repo_and_pr_number(pr_url)
        repo = self.github.get_repo(repo_name)
        pr = repo.get_pull(number=pr_number)
        pr.create_review(body=feedback, event="COMMENT")

    def merge_pr(self, pr_url: str) -> None:
        """
        Merges a pull request.
        """
        repo_name, pr_number = self._extract_repo_and_pr_number(pr_url)
        repo = self.github.get_repo(repo_name)
        pr = repo.get_pull(number=pr_number)
        pr.merge()

    def scan_for_malicious_code(self, pr_url: str) -> bool:
        """
        Scans a pull request for malicious code.
        """
        # This is a placeholder. A real implementation would involve a more
        # sophisticated scanning mechanism.
        return False

    def _extract_repo_and_issue_number(self, url: str) -> tuple[str, int]:
        parts = url.split("/")
        return f"{parts[-4]}/{parts[-3]}", int(parts[-1])

    def _extract_repo_and_pr_number(self, url: str) -> tuple[str, int]:
        parts = url.split("/")
        return f"{parts[-4]}/{parts[-3]}", int(parts[-1])
