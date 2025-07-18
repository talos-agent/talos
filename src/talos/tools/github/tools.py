from github import Github
from typing import Any


class GithubTools:
    def __init__(self, token: str):
        self.github = Github(token)

    def get_open_issues(self, user: str, project: str) -> "list[dict[str, Any]]":
        repo = self.github.get_repo(f"{user}/{project}")
        return [
            {"number": issue.number, "title": issue.title, "url": issue.html_url}
            for issue in repo.get_issues(state="open")
        ]

    def get_issue_comments(self, user: str, project: str, issue_number: int) -> "list[dict[str, Any]]":
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

    def reply_to_issue(self, user: str, project: str, issue_number: int, comment: str) -> None:
        repo = self.github.get_repo(f"{user}/{project}")
        issue = repo.get_issue(number=issue_number)
        issue.create_comment(comment)

    def get_pr_files(self, user: str, project: str, pr_number: int) -> "list[str]":
        repo = self.github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        return [file.filename for file in pr.get_files()]

    def get_project_structure(self, user: str, project: str, path: str = "") -> "list[str]":
        repo = self.github.get_repo(f"{user}/{project}")
        contents = repo.get_contents(path)
        if isinstance(contents, list):
            return [content.path for content in contents]
        return [contents.path]

    def get_file_content(self, user: str, project: str, filepath: str) -> str:
        repo = self.github.get_repo(f"{user}/{project}")
        content = repo.get_contents(filepath)
        if isinstance(content, list):
            raise ValueError("Path is a directory, not a file.")
        return content.decoded_content.decode()

    def merge_pr(self, user: str, project: str, pr_number: int) -> None:
        repo = self.github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.merge()

    def review_pr(self, user: str, project: str, pr_number: int, feedback: str) -> None:
        repo = self.github.get_repo(f"{user}/{project}")
        pr = repo.get_pull(number=pr_number)
        pr.create_review(body=feedback, event="COMMENT")
