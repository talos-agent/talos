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
        report = response.answers[0]

        # Extract the score from the report
        try:
            score_line = next(line for line in report.split("\\n") if "average sentiment score" in line)
            score = float(score_line.split("is ")[1].split(" ")[0])
        except (StopIteration, IndexError, ValueError):
            score = -1

        return {"score": score, "report": report}
