import random
from typing import Any

from pydantic import ConfigDict

from talos.services.abstract.twitter import TwitterPersona
from talos.services.proposals.models import QueryResponse
from talos.tools.twitter_client import TweepyClient, TwitterClient


class TwitterPersonaService(TwitterPersona):
    """
    A service for generating a persona prompt for a Twitter user.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    twitter_client: TwitterClient | None = None

    def __init__(self, twitter_client: TwitterClient | None = None, **data: Any):
        super().__init__(**data)
        self.twitter_client = twitter_client or TweepyClient()

    @property
    def name(self) -> str:
        return "twitter_persona"

    def run(self, **kwargs: Any) -> QueryResponse:
        if not self.twitter_client:
            self.twitter_client = TweepyClient()
        username = kwargs.get("username")
        if not username:
            raise ValueError("Username must be provided.")
        user_timeline = self.twitter_client.get_user_timeline(username)
        user_mentions = self.twitter_client.get_user_mentions(username)

        # This is a simplified analysis. A more sophisticated implementation would
        # use NLP to analyze the user's tone, style, and topics.
        if not user_timeline:
            return QueryResponse(answers=[f"Could not find any tweets for user {username}"])

        # Create a prompt that describes the user's voice and style.
        prompt = (
            f"Emulate the voice and style of the Twitter user '{username}'. "
            "They are known for their witty and sarcastic tweets, often using humor to make a point. "
            "They frequently tweet about technology and current events. "
            "Here are some examples of their tweets:\n\n"
        )
        for tweet in random.sample(user_timeline, min(len(user_timeline), 3)):
            prompt += f"- '{tweet.text}'\n"

        prompt += "\nHere are some examples of how they reply to others:\n\n"
        for tweet in random.sample(user_mentions, min(len(user_mentions), 2)):
            prompt += f"- Replying to @{tweet.in_reply_to_screen_name}: '{tweet.text}'\n"

        prompt += "\nNow, write a tweet in the same voice and style."

        return QueryResponse(answers=[prompt])
