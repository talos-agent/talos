from talos.disciplines.abstract.github import GitHub


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

    def merge_pr(self, pr_url: str) -> None:
        """
        Merges a pull request.
        """
        print(f"Merging PR: {pr_url}")

    def scan_for_malicious_code(self, pr_url: str) -> bool:
        """
        Scans a pull request for malicious code.
        """
        print(f"Scanning PR for malicious code: {pr_url}")
        return False
