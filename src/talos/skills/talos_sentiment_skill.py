from typing import Any

from talos.services.talos_sentiment import TalosSentimentService
from talos.skills.base import Skill


class TalosSentimentSkill(Skill):
    """
    A skill for analyzing the sentiment of tweets about Talos.
    """

    def __init__(self):
        super().__init__()
        self.sentiment_service = TalosSentimentService()

    @property
    def name(self) -> str:
        return "talos_sentiment_skill"

    def run(self, **kwargs: Any) -> Any:
        """
        Gets the sentiment of tweets that match a search query.

        Returns:
            A dictionary with the following keys:
            - "score": The average sentiment score, from 0 to 100.
            - "report": A detailed report of the sentiment analysis.
        """
        search_query = kwargs.get("search_query", "talos")
        response = self.sentiment_service.analyze_sentiment(search_query=search_query)
        return {"score": response.score, "report": response.answers[0]}
