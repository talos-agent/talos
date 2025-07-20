from talos.services.abstract.github import GitHub
from talos.tools.github import GithubTools
from langchain_core.language_models import BaseLanguageModel
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


class GitHubService(GitHub):
    """
    A discipline for interacting with GitHub using PyGithub.
    """

    def __init__(self, llm: BaseLanguageModel, token: str | None):
        super().__init__(llm, token)
        self.tools = GithubTools(token)

    @property
    def name(self) -> str:
        return "github"

    def reply_to_issues(self, user: str, project: str) -> None:
        """
        Replies to issues that are pending Talos feedback.
        """
        issues = self.tools.get_open_issues(user, project)
        for issue in issues:
            # A more sophisticated check would be needed to determine if an issue
            # is pending Talos feedback.
            if "talos" in issue["title"].lower():
                comments = self.tools.get_issue_comments(user, project, issue["number"])
                prompt = PromptTemplate(
                    template="""
                    The following is an issue that needs a response:
                    {issue}

                    Here are the comments on the issue:
                    {comments}

                    Please provide a response to the issue.
                    """,
                    input_variables=["issue", "comments"],
                )
                chain = LLMChain(llm=self.llm, prompt=prompt)
                response = chain.run(issue=issue["title"], comments=comments)
                self.tools.reply_to_issue(user, project, issue["number"], response)

    def review_pull_requests(self, user: str, project: str) -> None:
        """
        Reviews pending pull requests to determine if they're ready for approval or not.
        """
        # This is a placeholder. A real implementation would need to get all open PRs.
        pass

    def scan(self, user: str, project: str) -> str:
        """
        Reviews the code in a repository.
        """
        # This is a placeholder. A real implementation would need to get all files
        # and scan them.
        return "Scan complete."

    def reference_code(self, user: str, project: str, query: str) -> str:
        """
        Looks at the directory structure and any files in the repository to answer a query.
        """
        structure = self.tools.get_project_structure(user, project)
        prompt = PromptTemplate(
            template="""
            The following is the structure of the project:
            {structure}

            Please answer the following query about the code:
            {query}
            """,
            input_variables=["structure", "query"],
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)
        return chain.run(structure=structure, query=query)

    def update_summary(self, user: str, project: str) -> None:
        """
        Updates the SUMMARY.md for a repo to make it easier to review it.
        """
        # This is a placeholder. A real implementation would need to get all files
        # and generate a summary.
        pass
