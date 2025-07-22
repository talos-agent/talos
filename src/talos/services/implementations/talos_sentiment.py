import json
from datetime import datetime, timezone
from typing import Any

from pydantic import ConfigDict

from talos.prompts.prompt_managers.file_prompt_manager import FilePromptManager
from talos.services.abstract.talos_sentiment import TalosSentiment
from talos.services.proposals.models import QueryResponse
from talos.tools.twitter_client import TweepyClient
from talos.utils.llm import LLMClient


class TalosSentimentService(TalosSentiment):
    """
    A service for analyzing the sentiment of tweets about Talos.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    prompt_manager = FilePromptManager("src/talos/prompts")
    sentiment_prompt = prompt_manager.get_prompt("talos_sentiment_prompt")
    summary_prompt = prompt_manager.get_prompt("talos_sentiment_summary_prompt")

    @property
    def name(self) -> str:
        return "talos_sentiment"

    def run(self, **kwargs: Any) -> QueryResponse:
        if self.sentiment_prompt is None:
            raise ValueError("Sentiment prompt not found")
        if self.summary_prompt is None:
            raise ValueError("Summary prompt not found")
        twitter_client = TweepyClient()
        llm_client = LLMClient(api_key="dummy")
        search_query = kwargs.get("search_query", "talos")
        tweets = twitter_client.search_tweets(search_query)

        if not tweets:
            return QueryResponse(answers=["No tweets found for the given query."], score=None)

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
        prompt = self.sentiment_prompt.format(tweets=json.dumps(tweet_data))
        response = llm_client.reasoning(prompt)
        try:
            sentiments = json.loads(response)["sentiments"]
        except (json.JSONDecodeError, KeyError):
            return QueryResponse(answers=["Could not analyze the sentiment of any tweets."], score=None)

        if not sentiments:
            return QueryResponse(answers=["Could not analyze the sentiment of any tweets."], score=None)

        if not sentiments:
            return QueryResponse(answers=["Could not analyze the sentiment of any tweets."], score=None)

        total_weight = 0
        weighted_score = 0
        for i, sentiment in enumerate(sentiments):
            tweet = tweet_data[i]
            # Simple weighting scheme, can be adjusted
            weight = (1 / (tweet["age_in_days"] + 1)) * (tweet["followers"] + 1) * (tweet["engagement"] + 1)
            weighted_score += sentiment["score"] * weight
            total_weight += weight

        average_score = weighted_score / total_weight if total_weight > 0 else 0

        summary_prompt = self.summary_prompt.format(results=json.dumps(sentiments))
        summary = llm_client.reasoning(summary_prompt)

        report = f"Searched for '{search_query}' and analyzed {len(sentiments)} tweets.\\n"
        report += f"The weighted average sentiment score is {average_score:.2f} out of 100.\\n\\n"
        report += f"**Summary:** {summary}\\n\\n"
        report += "Here are some of the tweets that were analyzed:\\n"
        for i, sentiment in enumerate(sentiments[:5]):
            tweet = tweet_data[i]
            report += f"- **@{tweet['author']}** ({tweet['followers']} followers, {tweet['engagement']} engagement, {tweet['age_in_days']} days old): {sentiment['explanation']}\\n"

        return QueryResponse(answers=[report], score=average_score)
