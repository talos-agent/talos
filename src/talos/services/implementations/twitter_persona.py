import random
from typing import Any

from langchain_openai import ChatOpenAI
from pydantic import ConfigDict, Field

from talos.prompts.prompt_manager import PromptManager
from talos.services.abstract.twitter import TwitterPersona
from talos.services.proposals.models import QueryResponse
from talos.tools.twitter_client import TweepyClient, TwitterClient


class TwitterPersonaService(TwitterPersona):
    """
    A service for generating a persona prompt for a Twitter user.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    twitter_client: TwitterClient = Field(default_factory=TweepyClient)
    prompt_manager: PromptManager = Field(default_factory=PromptManager)
    llm: Any = Field(default_factory=ChatOpenAI)

    @property
    def name(self) -> str:
        return "twitter_persona"

    def run(self, **kwargs: Any) -> QueryResponse:
        username = kwargs.get("username")
        if not username:
            raise ValueError("Username must be provided.")
        user_timeline = self.twitter_client.get_user_timeline(username)
        user_mentions = self.twitter_client.get_user_mentions(username)

        if not user_timeline:
            return QueryResponse(answers=[f"Could not find any tweets for user {username}"])

        tweets = ""
        for tweet in random.sample(user_timeline, min(len(user_timeline), 20)):
            tweets += f"- '{tweet.text}'\n"

        replies = ""
        for tweet in random.sample(user_mentions, min(len(user_mentions), 5)):
            if tweet.in_reply_to_status_id:
                try:
                    original_tweet = self.twitter_client.get_tweet(tweet.in_reply_to_status_id)
                    replies += f"- In reply to @{original_tweet.user.screen_name}: '{original_tweet.text}'\n"
                    replies += f"  - @{username}'s reply: '{tweet.text}'\n\n"
                except Exception:
                    replies += f"- Replying to @{tweet.in_reply_to_screen_name}: '{tweet.text}'\n"

        prompt = self.prompt_manager.get_prompt("twitter_persona_prompt")
        if not prompt:
            raise ValueError("Could not find prompt 'twitter_persona_prompt'")
        formatted_prompt = prompt.format(username=username, tweets=tweets, replies=replies)

        response = self.llm.invoke(formatted_prompt)

        return QueryResponse(answers=[response.content], score=None)
