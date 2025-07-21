from __future__ import annotations

import json
from typing import Any

from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import PromptTemplate
from pydantic import ConfigDict

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.single_prompt_manager import SinglePromptManager
from talos.services.abstract.execution_planner import ExecutionPlanner
from talos.services.proposals.models import Plan, Question


def get_default_execution_planner_prompt() -> Prompt:
    with open("src/talos/prompts/execution_planner_prompt.json") as f:
        prompt_data = json.load(f)
    return Prompt(
        name=prompt_data["name"],
        template=prompt_data["template"],
        input_variables=prompt_data["input_variables"],
    )


class ExecutionPlannerService(ExecutionPlanner):
    """
    A LangChain-based agent for generating execution plans.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    llm: BaseLanguageModel
    prompt_manager: PromptManager = SinglePromptManager(get_default_execution_planner_prompt())
    rag_dataset: Any | None = None
    tools: list[Any] | None = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)

    def run(self, **kwargs: Any) -> Plan:
        if "question" in kwargs:
            return self.generate_plan(kwargs["question"])
        raise ValueError("Missing required arguments: question")

    def generate_plan(self, question: Question) -> Plan:
        """
        Generates a plan for execution based on a question and feedback.
        """
        prompt = self.prompt_manager.get_prompt("execution_planner_prompt")
        if not prompt:
            raise ValueError("Prompt 'execution_planner_prompt' not found.")
        prompt_template = PromptTemplate(
            template=prompt.template,
            input_variables=prompt.input_variables,
        )
        chain = prompt_template | self.llm
        feedback_str = "\n".join([f"- {f.delegate}: {f.feedback}" for f in question.feedback])
        response = chain.invoke({"question": question.text, "feedback": feedback_str})
        return Plan(plan=response.content)
