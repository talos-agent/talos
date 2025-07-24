from typing import Any

from talos.services.implementations.talos_sentiment import TalosSentimentService
from talos.skills.base import Skill


class TalosSentimentSkill(Skill):
    """
    A skill for analyzing the sentiment of tweets about Talos.
    """

    sentiment_service: TalosSentimentService

    @property
    def name(self) -> str:
        return "talos_sentiment_skill"

    def run(self, **kwargs: Any) -> Any:
        """
        Gets the sentiment of tweets that match a search query.

        Args:
            search_query: The query to search for tweets
            start_time: Optional datetime filter in ISO 8601 format (e.g., "2023-01-01T00:00:00Z")

        Returns:
            A dictionary with the following keys:
            - "score": The average sentiment score, from 0 to 100.
            - "report": A detailed report of the sentiment analysis.
        """
        search_query = kwargs.get("search_query", "talos")
        start_time = kwargs.get("start_time")
        response = self.sentiment_service.analyze_sentiment(search_query=search_query, start_time=start_time)
        return {"score": response.score, "report": response.answers[0]}
