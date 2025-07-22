import json
from datetime import datetime, timezone
from typing import Any

from pydantic import ConfigDict

from talos.prompts.prompt import Prompt
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.base import Service
from talos.services.models import TwitterSentimentResponse
from talos.tools.twitter_client import TweepyClient
from talos.utils.llm import LLMClient


class TalosSentimentService(Service):
    """
    A service for analyzing the sentiment of tweets about Talos.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self):
        self.prompt_manager = FilePromptManager("src/talos/prompts")
        self.twitter_client = TweepyClient()
        self.llm_client = LLMClient(api_key="dummy")

    @property
    def name(self) -> str:
        return "talos_sentiment"

    def analyze_sentiment(self, **kwargs: Any) -> TwitterSentimentResponse:
        sentiment_prompt_obj: Prompt | None = self.prompt_manager.get_prompt(
            "talos_sentiment_single_prompt"
        )
        if sentiment_prompt_obj is None:
            raise ValueError("Sentiment prompt not found")
        sentiment_prompt = sentiment_prompt_obj.template
        search_query = kwargs.get("search_query", "talos")
        tweets = self.twitter_client.search_tweets(search_query)

        if not tweets:
            return TwitterSentimentResponse(
                answers=["No tweets found for the given query."], score=None
            )

        tweet_data = [
            {
                "text": tweet.text,
                "author": tweet.author.screen_name,
                "followers": tweet.author.followers_count,
                "engagement": tweet.retweet_count + tweet.favorite_count,
                "age_in_days": (datetime.now(timezone.utc) - tweet.created_at).days,
            }
            for tweet in tweets
        ]
        prompt = sentiment_prompt.format(tweets=json.dumps(tweet_data))
        response = self.llm_client.reasoning(prompt)
        try:
            response_data = json.loads(response)
            score = response_data["score"]
            report = response_data["report"]
        except (json.JSONDecodeError, KeyError):
            return TwitterSentimentResponse(
                answers=["Could not analyze the sentiment of any tweets."], score=None
            )

        return TwitterSentimentResponse(answers=[report], score=score)
