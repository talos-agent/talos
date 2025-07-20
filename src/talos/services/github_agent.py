from __future__ import annotations

import json
from typing import Any

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic.types import SecretStr

from talos.tools.github.tools import GithubTools


class GithubPRReviewAgent:
    """
    An agent that reviews a pull request and provides feedback.
    """

    def __init__(self, token: str):
        github_tools = GithubTools(token=token)
        self.tools = [
            tool(github_tools.get_project_structure),
            tool(github_tools.get_file_content),
        ]
        self.llm = ChatOpenAI(api_key=SecretStr(token))
        with open("src/talos/prompts/github_pr_review_prompt.json") as f:
            prompt_config = json.load(f)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_config["template"],
                ),
                ("user", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools)

    def run(self, **kwargs: Any) -> Any:
        return self.agent_executor.invoke(kwargs)
