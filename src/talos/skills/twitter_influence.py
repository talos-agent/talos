from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import ConfigDict, Field

from talos.core.memory import Memory
from talos.models.proposals import QueryResponse
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill
from talos.tools.general_influence_evaluator import GeneralInfluenceEvaluator
from talos.tools.twitter_client import TweepyClient, TwitterClient


class TwitterInfluenceSkill(Skill):
    """
    A skill for analyzing general Twitter influence and perception.
    Evaluates any Twitter account for influence metrics including follower count,
    engagement rates, authenticity, credibility, and content quality.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    twitter_client: TwitterClient = Field(default_factory=TweepyClient)
    prompt_manager: PromptManager = Field(default_factory=lambda: FilePromptManager("src/talos/prompts"))
    llm: Any = Field(default_factory=ChatOpenAI)
    memory: Memory | None = Field(default=None)
    evaluator: GeneralInfluenceEvaluator | None = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        if self.memory is None:
            embeddings = OpenAIEmbeddings()
            memory_path = Path("data/influence_memory.json")
            self.memory = Memory(file_path=memory_path, embeddings_model=embeddings, auto_save=True)

        if self.evaluator is None:
            file_prompt_manager = self.prompt_manager if isinstance(self.prompt_manager, FilePromptManager) else FilePromptManager("src/talos/prompts")
            self.evaluator = GeneralInfluenceEvaluator(self.twitter_client, self.llm, file_prompt_manager)

    @property
    def name(self) -> str:
        return "twitter_influence_skill"

    def run(self, **kwargs: Any) -> QueryResponse:
        username = kwargs.get("username")
        if not username:
            raise ValueError("Username must be provided.")

        username = username.lstrip("@")

        try:
            user = self.twitter_client.get_user(username)

            assert self.evaluator is not None
            evaluation_result = self.evaluator.evaluate(user)

            memory_description = f"General influence evaluation for @{username}"
            memory_metadata = {
                "username": username,
                "evaluation_score": evaluation_result.score,
                "evaluation_data": evaluation_result.additional_data,
                "user_id": user.id,
                "followers_count": user.public_metrics.followers_count,
                "evaluation_type": "general_influence",
            }

            assert self.memory is not None
            self.memory.add_memory(memory_description, memory_metadata)

            prompt = self.prompt_manager.get_prompt("general_influence_analysis_prompt")
            if not prompt:
                analysis = f"General influence analysis for @{username}: Score {evaluation_result.score}/100"
            else:
                formatted_prompt = prompt.format(
                    username=username,
                    score=evaluation_result.score,
                    evaluation_data=evaluation_result.additional_data,
                    followers_count=user.public_metrics.followers_count,
                )
                response = self.llm.invoke(formatted_prompt)
                analysis = response.content

            return QueryResponse(answers=[analysis])

        except Exception as e:
            return QueryResponse(answers=[f"Error analyzing @{username}: {str(e)}"])
