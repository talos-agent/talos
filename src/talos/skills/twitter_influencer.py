from typing import Any
from pathlib import Path

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from pydantic import ConfigDict, Field

from talos.models.proposals import QueryResponse
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill
from talos.tools.twitter_client import TweepyClient, TwitterClient
from talos.tools.crypto_influencer_evaluator import CryptoInfluencerEvaluator
from talos.core.memory import Memory


class TwitterInfluencerSkill(Skill):
    """
    A skill for analyzing crypto Twitter influencers and storing long-term evaluations.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    twitter_client: TwitterClient = Field(default_factory=TweepyClient)
    prompt_manager: FilePromptManager = Field(default_factory=lambda: FilePromptManager("src/talos/prompts"))
    llm: Any = Field(default_factory=ChatOpenAI)
    memory: Memory | None = Field(default=None)
    evaluator: CryptoInfluencerEvaluator | None = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        if self.memory is None:
            embeddings = OpenAIEmbeddings()
            memory_path = Path("data/influencer_memory.json")
            self.memory = Memory(
                file_path=memory_path,
                embeddings_model=embeddings,
                auto_save=True
            )
        
        if self.evaluator is None:
            self.evaluator = CryptoInfluencerEvaluator(self.twitter_client)

    @property
    def name(self) -> str:
        return "twitter_influencer_skill"

    def run(self, **kwargs: Any) -> QueryResponse:
        username = kwargs.get("username")
        if not username:
            raise ValueError("Username must be provided.")
        
        username = username.lstrip('@')
        
        try:
            user = self.twitter_client.get_user(username)
            
            assert self.evaluator is not None
            evaluation_result = self.evaluator.evaluate(user)
            
            memory_description = f"Crypto influencer evaluation for @{username}"
            memory_metadata = {
                "username": username,
                "evaluation_score": evaluation_result.score,
                "evaluation_data": evaluation_result.additional_data,
                "user_id": user.id,
                "followers_count": user.followers_count,
                "evaluation_type": "crypto_influencer"
            }
            
            assert self.memory is not None
            self.memory.add_memory(memory_description, memory_metadata)
            
            prompt = self.prompt_manager.get_prompt("crypto_influencer_analysis_prompt")
            if not prompt:
                analysis = f"Crypto influencer analysis for @{username}: Score {evaluation_result.score}/100"
            else:
                formatted_prompt = prompt.format(
                    username=username,
                    score=evaluation_result.score,
                    evaluation_data=evaluation_result.additional_data,
                    followers_count=user.followers_count
                )
                response = self.llm.invoke(formatted_prompt)
                analysis = response.content
            
            return QueryResponse(answers=[analysis])
            
        except Exception as e:
            return QueryResponse(answers=[f"Error analyzing @{username}: {str(e)}"])
