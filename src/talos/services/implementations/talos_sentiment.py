import json
from datetime import datetime, timezone
from typing import Optional

from pydantic import ConfigDict

from talos.models.services import TwitterSentimentResponse
from talos.prompts.prompt import Prompt
from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.service import Service
from talos.tools.twitter_client import TweepyClient
from talos.utils.llm import LLMClient


class TalosSentimentService(Service):
    """
    A service for analyzing the sentiment of tweets about Talos.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    prompt_manager: FilePromptManager
    twitter_client: TweepyClient
    llm_client: LLMClient

    @property
    def name(self) -> str:
        return "talos_sentiment"

    def analyze_sentiment(self, search_query: str = "talos", start_time: Optional[str] = None) -> TwitterSentimentResponse:
        sentiment_prompt_obj: Prompt | None = self.prompt_manager.get_prompt("talos_sentiment_single_prompt")
        if sentiment_prompt_obj is None:
            raise ValueError("Sentiment prompt not found")
        sentiment_prompt = sentiment_prompt_obj.template
        tweets = self.twitter_client.search_tweets(search_query, start_time=start_time)

        if not tweets or not tweets.data:
            return TwitterSentimentResponse(answers=["No tweets found for the given query."], score=None)

        users = {user["id"]: user for user in tweets.includes.get("users", [])} if tweets.includes else {}
        
        tweet_data = []
        for tweet in tweets.data:
            author_id = tweet.author_id
            author = users.get(author_id, {})
            
            followers = author.get("public_metrics", {}).get("followers_count", 1)
            total_engagement = (tweet.public_metrics.get("like_count", 0) + 
                              tweet.public_metrics.get("retweet_count", 0) + 
                              tweet.public_metrics.get("reply_count", 0) + 
                              tweet.public_metrics.get("quote_count", 0))
            engagement_rate = total_engagement / max(followers, 1) * 100
            
            tweet_data.append({
                "text": tweet.text,
                "author": author.get("username", "unknown"),
                "followers": followers,
                "likes": tweet.public_metrics.get("like_count", 0),
                "retweets": tweet.public_metrics.get("retweet_count", 0),
                "replies": tweet.public_metrics.get("reply_count", 0),
                "quotes": tweet.public_metrics.get("quote_count", 0),
                "total_engagement": total_engagement,
                "engagement_rate": round(engagement_rate, 2),
                "age_in_days": (datetime.now(timezone.utc) - datetime.fromisoformat(tweet.created_at.replace('Z', '+00:00'))).days,
            })
        prompt = sentiment_prompt.format(tweets=json.dumps(tweet_data))
        response = self.llm_client.reasoning(prompt)
        try:
            response_data = json.loads(response)
            score = response_data["score"]
            report = response_data["report"]
        except (json.JSONDecodeError, KeyError):
            return TwitterSentimentResponse(answers=["Could not analyze the sentiment of any tweets."], score=None)

        return TwitterSentimentResponse(answers=[report], score=score)
