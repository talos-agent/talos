from __future__ import annotations

import json
from typing import Any

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from pydantic import PrivateAttr
from pydantic.types import SecretStr

from talos.services.abstract.service import Service
from talos.tools.github.tools import GithubTools


class GithubPRReviewAgent(Service):
    """
    An agent that reviews a pull request and provides feedback.
    """

    token: str
    _agent_executor: AgentExecutor = PrivateAttr()

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        github_tools = GithubTools(token=self.token)
        tools = [
            tool(github_tools.get_project_structure),
            tool(github_tools.get_file_content),
        ]
        llm = ChatOpenAI(api_key=SecretStr(self.token))
        with open("src/talos/prompts/github_pr_review_prompt.json") as f:
            prompt_config = json.load(f)
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_config["template"],
                ),
                ("user", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        agent = create_openai_tools_agent(llm, tools, prompt)
        self._agent_executor = AgentExecutor(agent=agent, tools=tools)

    @property
    def name(self) -> str:
        return "github_pr_review_agent"

    def run(self, **kwargs: Any) -> Any:
        return self._agent_executor.invoke(kwargs)
