import random
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import ConfigDict, Field

from talos.models.twitter import TwitterPersonaResponse
from talos.prompts.prompt_manager import PromptManager
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.skills.base import Skill
from talos.tools.twitter_client import TweepyClient, TwitterClient


class TwitterPersonaSkill(Skill):
    """
    A skill for generating a persona prompt for a Twitter user.

    This skill takes a Twitter username as input and generates a persona prompt
    based on the user's recent tweets and replies. It uses a large language
    model (LLM) to generate the persona.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    twitter_client: TwitterClient = Field(default_factory=TweepyClient)
    prompt_manager: PromptManager = Field(default_factory=lambda: FilePromptManager("src/talos/prompts"))
    llm: Any = Field(default_factory=lambda: ChatOpenAI(model="gpt-4o"))

    @property
    def name(self) -> str:
        return "twitter_persona_skill"

    def run(self, **kwargs: Any) -> TwitterPersonaResponse:
        username = kwargs.get("username")
        if not username:
            raise ValueError("Username must be provided.")
        user_timeline = self.twitter_client.get_user_timeline(username)
        user_mentions = self.twitter_client.get_user_mentions(username)

        if not user_timeline:
            return TwitterPersonaResponse(
                report=f"Could not find any tweets for user {username}",
                topics=[],
                style=[]
            )

        tweets = ""
        for tweet in random.sample(user_timeline, min(len(user_timeline), 20)):
            tweets += f"- '{tweet.text}'\n"

        replies = ""
        for tweet in random.sample(user_mentions, min(len(user_mentions), 5)):
            replied_to_id = tweet.get_replied_to_id()
            if replied_to_id:
                try:
                    original_tweet = self.twitter_client.get_tweet(replied_to_id)
                    replies += f"- In reply to someone: '{original_tweet.text}'\n"
                    replies += f"  - @{username}'s reply: '{tweet.text}'\n\n"
                except Exception:
                    replies += f"- Replying to someone: '{tweet.text}'\n"

        prompt = self.prompt_manager.get_prompt("twitter_persona_prompt")
        if not prompt:
            raise ValueError("Could not find prompt 'twitter_persona_prompt'")
        formatted_prompt = prompt.format(username=username, tweets=tweets, replies=replies)

        structured_llm = self.llm.with_structured_output(TwitterPersonaResponse)
        response = structured_llm.invoke(formatted_prompt)

        return response
