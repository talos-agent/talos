from github import Github
from talos.disciplines.abstract.github import GitHub
from typing import List, Dict, Any


class PyGithubDiscipline(GitHub):
    """
    A discipline for interacting with GitHub using PyGithub.
    """

    def __init__(self, token: str):
        self.github = Github(token)

    def read_issue(self, user: str, project: str, issue_number: int) -> str:
        """
        Reads a GitHub issue.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        return issue.body

    def reply_to_issue(self, user: str, project: str, issue_number: int, comment: str) -> None:
        """
        Replies to a GitHub issue.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)

    def review_pr(self, user: str, project: str, pr_number: int, feedback: str) -> None:
        """
        Reviews a pull request.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_review(body=feedback, event="COMMENT")

    def merge_pr(self, user: str, project: str, pr_number: int) -> None:
        """
        Merges a pull request.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.merge()

    def scan_for_malicious_code(self, user: str, project: str, pr_number: int) -> bool:
        """
        Scans a pull request for malicious code.
        """
        # This is a placeholder. A real implementation would involve a more
        # sophisticated scanning mechanism.
        return False

    def get_open_issues(self, user: str, project: str) -> List[Dict[str, Any]]:
        """
        Gets all open issues in a repository.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        return [
            {"number": issue.number, "title": issue.title, "url": issue.html_url}
            for issue in repo.get_issues(state="open")
        ]

    def get_issue_comments(self, user: str, project: str, issue_number: int) -> List[Dict[str, Any]]:
        """
        Gets all comments for an issue.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        comments = []
        for comment in issue.get_comments():
            comments.append(
                {
                    "user": comment.user.login,
                    "comment": comment.body,
                    "reply_to": None,  # PyGithub does not support this directly
                }
            )
        return comments

    def get_pr_files(self, user: str, project: str, pr_number: int) -> List[str]:
        """
        Gets all files in a pull request.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        return [file.filename for file in pr.get_files()]

    def get_project_structure(self, user: str, project: str, path: str = "") -> List[str]:
        """
        Gets the project structure.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        contents = repo.get_contents(path)
        if isinstance(contents, list):
            return [content.path for content in contents]
        return [contents.path]

    def get_file_content(self, user: str, project: str, filepath: str) -> str:
        """
        Gets the content of a file.
        """
        repo = self.github.get_repo(f"{user}/{project}")
        content = repo.get_contents(filepath)
        if isinstance(content, list):
            raise ValueError("Path is a directory, not a file.")
        return content.decoded_content.decode()
