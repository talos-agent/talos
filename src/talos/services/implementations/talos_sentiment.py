import json
from typing import Any

from pydantic import ConfigDict

from talos.services.abstract.talos_sentiment import TalosSentiment
from talos.services.proposals.models import QueryResponse
from talos.tools.twitter_client import TweepyClient
from talos.utils.llm import LLMClient


class TalosSentimentService(TalosSentiment):
    """
    A service for analyzing the sentiment of tweets about Talos.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def name(self) -> str:
        return "talos_sentiment"

    def run(self, **kwargs: Any) -> QueryResponse:
        twitter_client = TweepyClient()
        llm_client = LLMClient(api_key="dummy")
        search_query = kwargs.get("search_query", "talos")
        tweets = twitter_client.search_tweets(search_query)

        if not tweets:
            return QueryResponse(answers=["No tweets found for the given query."])

        sentiment_prompt = "Analyze the sentiment of the following tweet, returning a score from 0 to 100 (0 being very negative, 100 being very positive) and a brief explanation of your reasoning. Return your response as a JSON object with the keys 'score' and 'explanation'."
        sentiments = []
        for tweet in tweets:
            response = llm_client.reasoning(sentiment_prompt, tweet.text)
            try:
                sentiment_data = json.loads(response)
                sentiments.append(sentiment_data)
            except json.JSONDecodeError:
                # Handle cases where the LLM doesn't return valid JSON
                pass

        if not sentiments:
            return QueryResponse(answers=["Could not analyze the sentiment of any tweets."])

        average_score = sum(s["score"] for s in sentiments) / len(sentiments)
        report = f"Searched for '{search_query}' and analyzed {len(sentiments)} tweets.\\n"
        report += f"The average sentiment score is {average_score:.2f} out of 100.\\n\\n"
        report += "Here are some of the explanations:\\n"
        for s in sentiments[:5]:
            report += f"- {s['explanation']}\\n"

        return QueryResponse(answers=[report])
