from talos.services.implementations.talos_sentiment import TalosSentimentService


class TalosSentimentSkill:
    """
    A skill for analyzing the sentiment of tweets about Talos.
    """

    def __init__(self):
        self.sentiment_service = TalosSentimentService()

    def get_sentiment(self, search_query: str = "talos") -> dict:
        """
        Gets the sentiment of tweets that match a search query.

        Returns:
            A dictionary with the following keys:
            - "score": The average sentiment score, from 0 to 100.
            - "report": A detailed report of the sentiment analysis.
        """
        response = self.sentiment_service.run(search_query=search_query)
        return {"score": response.score, "report": response.answers[0]}
