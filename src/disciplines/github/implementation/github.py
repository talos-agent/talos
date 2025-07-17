from src.disciplines.github.abc.github_abc import GitHub


class GitHubDiscipline(GitHub):
    """
    A discipline for interacting with GitHub.
    """

    def read_issue(self, issue_url: str) -> str:
        """
        Reads a GitHub issue.
        """
        return f"Reading issue: {issue_url}"

    def reply_to_issue(self, issue_url: str, comment: str) -> None:
        """
        Replies to a GitHub issue.
        """
        print(f"Replying to issue {issue_url} with: {comment}")

    def review_pr(self, pr_url: str, feedback: str) -> None:
        """
        Reviews a pull request.
        """
        print(f"Reviewing PR {pr_url} with feedback: {feedback}")
