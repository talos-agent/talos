from abc import ABC, abstractmethod


class Twitter(ABC):
    """
    An abstract base class for a Twitter discipline.
    """

    @abstractmethod
    def read_posts(self, query: str) -> str:
        """
        Reads posts on Twitter that match a query.
        """
        pass

    @abstractmethod
    def post_tweet(self, tweet: str) -> None:
        """
        Posts a tweet.
        """
        pass

    @abstractmethod
    def reply_to_tweet(self, tweet_id: str, reply: str) -> None:
        """
        Replies to a tweet.
        """
        pass

    @abstractmethod
    def create_poll(self, question: str, options: list[str]) -> None:
        """
        Creates a poll on Twitter.
        """
        pass

    @abstractmethod
    def get_poll_results(self, poll_id: str) -> dict:
        """
        Gets the results of a poll.
        """
        pass

    @abstractmethod
    def get_all_replies(self, tweet_id: str) -> list[str]:
        """
        Gets all replies to a tweet.
        """
        pass
